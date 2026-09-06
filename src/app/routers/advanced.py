# =============================================================================
# routers/advanced.py  --  LEVEL 3 (ADVANCED) : the "hard" FastAPI features
# =============================================================================
# IMPLEMENTED HERE:
#   1. Redis caching        : cache expensive responses so repeated calls hit
#     memory (Redis) instead of recomputing. Great interview answer for
#     "how do you speed up a slow endpoint?"
#   2. Background tasks     : offload slow work (emails, file parsing) so the
#     client gets a fast response and work happens AFTER the response is sent.
#   3. File uploads         : accept multipart/form-data files, save them.
#   4. WebSockets           : real-time bidirectional communication.
#   5. Rate limiting        : per-user/per-IP sliding window via Redis.
#
# LEVEL MARKER: This is the most advanced file in the project — read it after
# basic.py and tasks.py.

import io
import json
import time
from typing import Any

import redis
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbDep
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/advanced", tags=["advanced"])

# A single shared Redis client (reused across all endpoints).
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# ===========================================================================
# 1) REDIS CACHING
# ===========================================================================
def cache_get_json(key: str) -> Any | None:
    """Fetch a cached JSON value. Returns parsed data or None on miss/expiry."""
    raw = redis_client.get(key)
    return json.loads(raw) if raw else None


def cache_set_json(key: str, value: Any, ttl: int = 60) -> None:
    # setex = "set with expiry". ttl seconds before the key auto-deletes.
    redis_client.setex(key, ttl, json.dumps(value))


@router.get("/cached-time", summary="Redis-cached slow computation")
def cached_time(db: DbDep, current_user: CurrentUser) -> dict:
    """Simulate an expensive/slow operation, cached in Redis for 30s.
       First call is slow (sleeps 3s), subsequent calls are instant (cache hit).
       KEY PATTERN: include a version/user prefix so you can invalidate."""
    key = f"current_user:{current_user.id}:cached_time"
    cached = cache_get_json(key)
    if cached is not None:
        return {"source": "cache", **cached}        # served from Redis

    # ... pretend this is a costly DB query / external API call ...
    time.sleep(3)
    value = {"computed_at": time.time(), "computed_by": current_user.email}
    cache_set_json(key, value, ttl=30)
    return {"source": "fresh", **value}             # served after recompute


@router.delete("/cache", summary="Invalidate a user's Redis cache")
def invalidate_cache(current_user: CurrentUser) -> dict:
    """Show cache invalidation: delete keys matching a user's prefix.
       (SCAN is safer than KEYS for large DBs, but keys* is fine for learning.)"""
    pattern = f"current_user:{current_user.id}:*"
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
    return {"deleted": len(keys)}


# ===========================================================================
# 2) BACKGROUND TASKS
# ===========================================================================
def _write_report(user: User, delay: float = 2.0) -> None:
    """Simulated slow job (would be: email, PDF gen, parsing, ML inference).
       Runs AFTER the response is returned to the client (fire-and-forget)."""
    time.sleep(delay)
    # In a real app you'd log / write to a file / call Celery.
    print(f"[background] report for {user.email} generated at {time.time()}")


@router.post("/reports/generate", summary="Start a background job")
def generate_report(background_tasks: BackgroundTasks, current_user: CurrentUser) -> dict:
    """Schedule the expensive job to run in the background.
       The endpoint returns IMMEDIATELY (fast response), then FastAPI runs
       _write_report after the response is sent.
       Caveat: this survives only for the current worker process. For durable
       jobs use Celery (see app/celery_app.py)."""
    background_tasks.add_task(_write_report, current_user)
    return {"status": "queued", "message": "Report will be generated in the background"}


# ===========================================================================
# 3) FILE UPLOAD
# ===========================================================================
@router.post("/upload", summary="Upload a file")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """Accept a multipart/form-data file upload.
       `UploadFile` streams the file (doesn't load it all into RAM at once).
       `await file.read()` reads bytes; file.filename gives the name.
       NOTE: async route + await -> non-blocking I/O while reading."""
    contents = await file.read()                 # bytes
    guessed_size = len(contents)
    # We don't really save it (would use a media dir + shutil.move) — just demo.
    return {
        "filename": file.filename,
        "content_type": file.content_type,       # e.g. image/png
        "size_bytes": guessed_size,
        "note": "In production, validate content-type/size and stream to disk",
    }


# ===========================================================================
# 4) WEBSOCKETS (real-time)
# ===========================================================================
# A WebSocket keeps a persistent TCP connection open so the server can PUSH
# messages to the client at any time (chat, live counters, notifications).
# Different HTTP-style: client connects to ws://... and both sides send frames.
class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []        # all live connections

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()                        # complete the handshake
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: str) -> None:
        for ws in self.active:
            await ws.send_text(message)          # push to every connected client


manager = ConnectionManager()


@router.websocket("/ws/echo/{client}")
async def websocket_echo(websocket: WebSocket, client: str) -> None:
    """Echo endpoint demonstrating the WebSocket lifecycle."""
    # manager.accept -> read frames in a loop -> close on disconnect
    await manager.connect(websocket)
    try:
        while True:                              # keep reading until closed
            incoming = await websocket.receive_text()
            await websocket.send_text(f"[{client}] got: {incoming}")
            await manager.broadcast(f"{client} said: {incoming}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)            # clean up the dead socket


# ===========================================================================
# 5) RATE LIMITING (Redis sliding window)
# ===========================================================================
def enforce_rate_limit(key: str, limit: int, window: int) -> None:
    """Sliding-window rate limit using a Redis counter with TTL.
       For every request we INCR a key; the key auto-expires after `window`s.
       If the count exceeds `limit`, we reject with HTTP 429 Too Many Requests.
       (Production might use PEXPIRE + pipeline for atomicity — simplified here.)"""
    current = redis_client.incr(key)             # +1, atomic
    if current == 1:
        redis_client.expire(key, window)         # set TTL on first request
    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {limit} per {window}s",
        )


@router.get("/rate-limited", summary="Redis rate-limited endpoint")
def rate_limited(current_user: CurrentUser) -> dict:
    """Each authenticated user may call this at most
       RATE_LIMIT_REQUESTS times per RATE_LIMIT_WINDOW seconds."""
    key = f"rate_limit:{current_user.id}"
    enforce_rate_limit(key, settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW)
    return {"ok": True, "user": current_user.email}


# A small Pydantic model to show request bodies + JSON in advanced route.
class Payload(BaseModel):
    message: str
    tags: list[str] = []


@router.post("/echo-json", summary="Echo a validated JSON body [ADVANCED]")
def echo_json(body: Payload, current_user: CurrentUser) -> dict:
    """Shows Pydantic validation in an advanced route + auth."""
    return {"received": body.model_dump(), "from": current_user.email}
