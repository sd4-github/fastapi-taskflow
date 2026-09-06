#!/usr/bin/env python3
"""
smoke_test.py  --  run the full app in-process (via TestClient) and verify
the ADVANCED Redis-backed features work end-to-end.

Usage:  /home/soumikd4/Desktop/code/interview-prep/1_fastapi_taskflow/.venv/bin/python smoke_test.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Point at the main dev DB (not the isolated test DB) so Redis effects persist.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://taskflow:taskflow@127.0.0.1:5432/taskflow",
)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import init_db  # noqa: E402
from app.main import app  # noqa: E402


def main() -> None:
    init_db()  # ensure tables exist
    client = TestClient(app)

    # --- register + login (get a token) ---
    email = "smoke@example.com"
    client.post("/auth/register", json={"email": email, "password": "secret123"})
    login = client.post("/auth/login", data={"username": email, "password": "secret123"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[ok] authenticated as", email)

    # --- Redis CACHING: first call slow, second call cached ---
    import time
    t0 = time.time()
    r1 = client.get("/advanced/cached-time", headers=headers)
    fresh_time = time.time() - t0
    assert r1.status_code == 200 and r1.json()["source"] == "fresh"
    t0 = time.time()
    r2 = client.get("/advanced/cached-time", headers=headers)
    cache_time = time.time() - t0
    assert r2.status_code == 200 and r2.json()["source"] == "cache"
    print(f"[ok] redis cache: fresh={fresh_time:.2f}s cached={cache_time:.2f}s")

    # --- BACKGROUND TASK (fire and forget) ---
    r3 = client.post("/advanced/reports/generate", headers=headers)
    assert r3.status_code == 200 and r3.json()["status"] == "queued"
    print("[ok] background task queued:", r3.json()["message"])

    # --- FILE UPLOAD ---
    r4 = client.post(
        "/advanced/upload",
        headers=headers,
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert r4.status_code == 200
    print("[ok] upload detected size:", r4.json()["size_bytes"], "bytes")

    # --- RATE LIMITING: allowed up to N, then 429 ---
    ok_requests = 0
    status_429 = None
    for _ in range(15):  # exceed the limit (5 per 60s) to trigger 429
        resp = client.get("/advanced/rate-limited", headers=headers)
        if resp.status_code == 200:
            ok_requests += 1
        else:
            status_429 = resp.status_code
            break
    assert ok_requests >= 1 and status_429 == 429, (ok_requests, status_429)
    print(f"[ok] rate limit: {ok_requests} ok then HTTP {status_429}")

    print("\nALL SMOKE TESTS PASSED (basic->advanced features verified)")


if __name__ == "__main__":
    main()
