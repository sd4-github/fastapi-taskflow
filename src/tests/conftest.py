# =============================================================================
# tests/conftest.py  --  pytest fixtures for the FastAPI project
# =============================================================================
# Pytest "fixtures" = reusable setup/teardown. Key patterns (interview):
#   * session/function/class scope control WHEN a fixture is created/reused.
#   * We override FastAPI's get_db dependency so tests hit a throwaway database
#     and roll back after each test (transaction isolation = no leftover rows).
#   * TestClient wraps the app to send real HTTP requests through the ASGI stack.

import os

# MUST set DATABASE_URL before importing the app/pydantic-settings so the
# Settings singleton reads the test DB URL.
os.environ["DATABASE_URL"] = "postgresql+psycopg2://taskflow:taskflow@127.0.0.1:5432/taskflow_test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import Base, engine, SessionLocal, get_db
from app.main import app


# Import models so Base.metadata knows all tables before create_all.
from app import models  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the whole test session, drop after."""
    Base.metadata.drop_all(bind=engine)   # fresh slate
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """A fresh DB session per test; rollback after so tests are isolated."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(connection)

    # Override the get_db dependency used by all endpoints.
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield session

    app.dependency_overrides.clear()
    transaction.rollback()                # undo everything this test did
    connection.close()


@pytest.fixture()
def client(db_session):
    """Build an HTTP client that routes through the app with the overridden DB."""
    return TestClient(app)
