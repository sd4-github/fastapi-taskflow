# =============================================================================
# tests/test_auth_tasks.py  --  tests for auth + authenticated task CRUD
# =============================================================================
# Shows the NEGATIVE path is tested too: unauthenticated requests must be 401.

from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str) -> str:
    """Helper: create a user, then return their bearer token."""
    client.post("/auth/register", json={"email": email, "password": "secret123"})
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": "secret123"},  # form fields!
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_register_then_login(client: TestClient):
    token = _register_and_login(client, "alice@example.com")
    assert token            # we got back a JWT


def test_duplicate_register_conflict(client: TestClient):
    email = "bob@example.com"
    client.post("/auth/register", json={"email": email, "password": "secret123"})
    second = client.post("/auth/register", json={"email": email, "password": "secret123"})
    assert second.status_code == 409   # duplicate email


def test_login_wrong_password(client: TestClient):
    client.post("/auth/register", json={"email": "c@example.com", "password": "secret123"})
    resp = client.post("/auth/login", data={"username": "c@example.com", "password": "WRONG"})
    assert resp.status_code == 401


def test_tasks_require_auth(client: TestClient):
    """Without a token, task endpoints must 401 (dependency rejection)."""
    resp = client.get("/tasks")
    assert resp.status_code == 401


def test_owner_can_only_see_own_tasks(client: TestClient):
    token_a = _register_and_login(client, "ownerA@example.com")
    token_b = _register_and_login(client, "ownerB@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # A creates a task
    created = client.post("/tasks", json={"title": "A's task"}, headers=headers_a)
    assert created.status_code == 201
    task_id = created.json()["id"]

    # B lists tasks -> must NOT see A's task (row-level isolation)
    b_list = client.get("/tasks", headers=headers_b).json()
    assert all(t["id"] != task_id for t in b_list["items"])


def test_task_crud_flow(client: TestClient):
    token = _register_and_login(client, "flow@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/tasks", json={"title": "learn", "priority": 3}, headers=headers)
    assert created.status_code == 201
    tid = created.json()["id"]

    # partial update (PATCH) only touches `done`
    patched = client.patch(f"/tasks/{tid}", json={"done": True}, headers=headers)
    assert patched.status_code == 200
    assert patched.json()["done"] is True
    assert patched.json()["title"] == "learn"      # unchanged by the patch

    deleted = client.delete(f"/tasks/{tid}", headers=headers)
    assert deleted.status_code == 204
