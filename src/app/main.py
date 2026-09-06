# =============================================================================
# main.py  --  FastAPI application entry point
# =============================================================================
# This is where we build the app, register routers, add middleware, and define
# global exception handlers. Run with:
#     .venv/bin/uvicorn app.main:app --reload
# (from the src/ directory)
#
# CONCEPTS (advanced):
#   * FastAPI() instance = the whole application.
#   * include_router()   : mount the sub-routers we built (basic/tasks/auth/...).
#   * middleware         : code that runs on EVERY request (before the route
#     handler). Great for logging, headers, CORS, timing, auth at the edge.
#   * exception_handler  : global handlers for custom errors (avoids try/except
#     duplication all over the code).
#   * lifespan           : startup/shutdown hooks (e.g. init DB, warm caches).

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.database import init_db
from app.routers import advanced, auth, basic, tasks


# ---------------------------------------------------------------------------
# LIFESPAN (startup + shutdown hooks)
# ---------------------------------------------------------------------------
# async context manager: the code BEFORE `yield` runs at startup, the code
# AFTER `yield` runs at shutdown. Modern replacement for deprecated on_event.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP: create tables if they don't exist (dev convenience) ---
    # In production, migrate with Alembic instead. This keeps first-run easy.
    init_db()
    print(f"[startup] {settings.APP_NAME} started, DB tables ensured")
    yield
    # --- SHUTDOWN: close pools, cancel jobs, etc. ---
    print("[shutdown] app is stopping")


# ---------------------------------------------------------------------------
# Create the application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI demo API: TaskFlow — teaches basics -> advanced features.",
    lifespan=lifespan,
    # To NOT show /docs in production you'd pass docs_url=None.
    # docs_url="/docs", redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------------
# CORS: allows browser-based (front-end) apps on OTHER origins to call this
# API. Without it, cross-origin JS requests from a React/Vue front-end would
# be blocked by the browser (the "Cross-Origin Request Blocked" error).
# In production, restrict origins to your actual front-end domain (NOT "*").
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # restrict in real apps!
    allow_credentials=True,
    allow_methods=["*"],              # GET/POST/PUT/DELETE/OPTIONS...
    allow_headers=["*"],
)


# Custom middleware example: a simple request logger + timing header.
# It prints method/path/duration for every request. Order matters —
# middleware added FIRST runs LAST for the request (it's a stack).
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time
    start = time.perf_counter()
    response = await call_next(request)          # forward to the route handler
    process_time = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    print(f"[mw] {request.method} {request.url.path} -> {process_time*1000:.2f}ms")
    return response


# ---------------------------------------------------------------------------
# GLOBAL EXCEPTION HANDLER (demo)
# ---------------------------------------------------------------------------
# Catches ANY exception, logs it, and returns a clean JSON 500 instead of a
# stack trace leaking to the client. Avoids duplicating try/except everywhere.
# (For true logging use a library like structlog / sentry.)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f"[error] {request.method} {request.url.path} -> {exc!r}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. We've logged it."},
    )


# ---------------------------------------------------------------------------
# Health check (ops / interview favourite)
# ---------------------------------------------------------------------------
@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness/readiness probe used by load balancers & k8s.
       Should be cheap and not require auth."""
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/", tags=["ops"])
def root() -> dict[str, str]:
    # .path lets us build URLs relative to this server instead of hardcoding.
    return {
        "message": "TaskFlow API — see /docs for interactive Swagger UI",
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# Register routers (each handles one concern)
# ---------------------------------------------------------------------------
app.include_router(basic.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(advanced.router)
