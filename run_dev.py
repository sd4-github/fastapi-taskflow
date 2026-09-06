#!/usr/bin/env python3
"""
run_dev.py  --  one-shot dev helper for the FastAPI project.

It ensures tables exist (init_db), then boots the ASGI server with uvicorn.
Usage:
    .venv/bin/python run_dev.py          # start on 127.0.0.1:8000
"""
import os
import sys

# Make `src` importable in-process so `import app` works without installing.
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def main() -> None:
    from app.core.database import init_db   # local import keeps this file light
    init_db()                                # ensure tables exist (dev only)
    print("Tables ensured. Starting uvicorn on 127.0.0.1:8000")
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
