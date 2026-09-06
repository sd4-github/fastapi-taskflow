# =============================================================================
# core/database.py  --  SQLAlchemy engine / session management
# =============================================================================
# KEY CONCEPTS (interview gold):
#   * ENGINE   : one object that manages the connection pool to Postgres.
#                Created ONCE and reused for the app's life.
#   * SESSION  : short-lived "unit of work" wrapping one transaction.
#                You get one per request, use it, and close it.
#   * DECLARATIVE BASE : the parent class every model inherits from.
#                It keeps a registry of all models (for metadata / migrations).
#
#   create_engine("postgresql+psycopg2://..."):
#     - pool_size=5  : keep 5 connections open (shared, not per request)
#     - pool_pre_ping=True : if a pooled conn went stale (DB restarted),
#                            check it with a cheap "ping" before using.
#   SessionLocal is a *session factory* ; calling SessionLocal() gives a new
#   session. This is better than sharing one session across threads.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# --- Engine ---------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,        # avoid broken pooled connections
    pool_size=5,               # base pool size
    max_overflow=10,           # allow up to 10 extra beyond pool_size
    echo=False,                # set True to print every SQL (great for learning!)
)

# --- Session factory ------------------------------------------------------
# bind=engine : sessions created from this factory use the engine above.
# autoflush=False : don't auto-send pending changes before each query
#                   (avoids surprising partial writes; flush explicitly).
# autocommit=False : wrap work in an explicit transaction we commit ourselves.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Declarative base ------------------------------------------------------
# Every ORM model inherits from Base. Alembic uses Base.metadata to know
# what tables to create in migrations.
Base = declarative_base()


# --- Dependency for FastAPI ------------------------------------------------
# This is a FastAPI *dependency*. FastAPI calls it before each request,
# yields a session, and ALWAYS runs the finally after the request finishes.
# This guarantees the session is closed even if the handler raises.
#
# Why `yield` instead of `return`? Because we need cleanup code (session.close())
# to run AFTER the request. Docs: "Dependencies with yield" — the code after
# yield runs after the response is built.
#
# yield is a generator-function pattern: FastAPI unwraps the single yielded
# value as the dependency result.
def get_db():
    db = SessionLocal()          # open a fresh session for this request
    try:
        yield db                 # hand the session to the endpoint
    finally:
        db.close()               # always release it back to the pool


# --- Helper to create tables (dev convenience) -----------------------------
def init_db():
    """Create all tables based on the models (no migrations).
       For learning you can run `./run_dev.py` which calls this.
       In production always use Alembic migrations instead."""
    from app import models  # noqa: F401  (import triggers model registration)
    Base.metadata.create_all(bind=engine)
