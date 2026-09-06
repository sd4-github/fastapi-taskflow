# =============================================================================
# tests/test_api.py  --  end-to-end tests through the HTTP layer
# =============================================================================
# Testing fundamentals (interview):
#   * We test THROUGH HTTP (TestClient) = tests the full stack: routing,
#     validation, dependencies, DB, serialization. "Black box" style.
#   * Status codes assert the contract (201 created, 401 unauthenticated...).
#   * Fixtures (client) are injected as function args.

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    """/health should be public and healthy."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_basic_hello(client: TestClient):
    """Basic level endpoint: should return a friendly message."""
    resp = client.get("/basic/hello")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello, world!"}


def test_basic_validation(client: TestClient):
    """FastAPI auto-validates: a negative price must be rejected with 422."""
    resp = client.post("/basic/items", json={"name": "x", "price": -5})
    # 422 Unprocessable Entity = validation error (Pydantic caught it)
    assert resp.status_code == 422


def test_basic_crud_flow(client: TestClient):
    """Create -> read -> list -> delete one item."""
    created = client.post("/basic/items", json={"name": "pen", "price": 1.5})
    assert created.status_code == 201
    item_id = created.json()["id"]

    got = client.get(f"/basic/items/{item_id}")
    assert got.status_code == 200
    assert got.json()["name"] == "pen"

    listed = client.get("/basic/items")
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    deleted = client.delete(f"/basic/items/{item_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/basic/items/{item_id}")
    assert missing.status_code == 404
