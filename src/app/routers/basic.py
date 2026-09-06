# =============================================================================
# routers/basic.py  --  LEVEL 1 (BASIC) : FastAPI fundamentals, no DB, no auth
# =============================================================================
# This file exists so you can learn the *surface* of FastAPI before touching
# databases. Run the app and open http://127.0.0.1:8000/docs
#
# CONCEPTS COVERED (basic):
#   * @app.get/post/put/delete  -- HTTP method decorators
#   * path parameters          -- /items/{item_id}
#   * query parameters         -- /items?skip=0&limit=10
#   * request body (Pydantic)  -- JSON sent by the client, auto-validated
#   * automatic OpenAPI docs   -- /docs and /redoc generated for free
#   * status codes             -- return HTTPStatus codes
#
# NEXT: see routers/tasks.py (LEVEL 2) for DB + dependencies.

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

# APIRouter groups routes. The main app includes sub-routers; each router can
# share a common URL prefix and tags (tags group endpoints in /docs).
router = APIRouter(prefix="/basic", tags=["basic-level"])


# --- A Pydantic model used only for the request body of an endpoint ----------
class Item(BaseModel):
    name: str = Field(..., min_length=1)       # required
    price: float = Field(..., gt=0)            # must be > 0
    in_stock: bool = True                      # optional w/ default


# An in-memory "database" (a plain dict). Demonstrates basics without SQL.
IN_MEMORY_ITEMS: dict[int, Item] = {}


# ---- BASIC 1: simplest possible endpoint ------------------------------------
# A GET route returning a string. Nothing simpler.
@router.get("/hello", summary="Say hello")
def hello() -> dict[str, str]:
    return {"message": "Hello, world!"}


# ---- BASIC 2: path parameter -------------------------------------------------
# Path parameters are named inside `{}` in the route and passed as function args.
# The `Path(ge=1)` validator ensures item_id is an int >= 1 (else FastAPI 422s).
@router.get("/items/{item_id}", summary="Fetch one item by id")
def get_item(item_id: int = Path(..., ge=1)) -> dict:
    item = IN_MEMORY_ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # We return a plain dict; FastAPI serializes it to JSON for us.
    return {"id": item_id, **item.model_dump()}


# ---- BASIC 3: query parameters -----------------------------------------------
# Parameters NOT in the path are auto-read from the query string (?a=1&b=2).
# Defaults make them optional. FastAPI validates types (int, int) for free.
@router.get("/items", summary="List items (query params demo)")
def list_items(
    skip: int = Query(0, ge=0),      # ?skip=0
    limit: int = Query(10, ge=1, le=100),  # ?limit=50
) -> dict:
    # enumerate + slicing mimics pagination (skip/limit pattern) in simple form.
    start = skip
    end = skip + limit
    # Build [{id, ...item}, ...] from the dict, sliced like a page of results.
    page = [
        {"id": i, **it.model_dump()}
        for i, it in list(IN_MEMORY_ITEMS.items())[start:end]
    ]
    return {"total": len(IN_MEMORY_ITEMS), "skip": skip, "limit": limit, "items": page}


# ---- BASIC 4: request body (POST) --------------------------------------------
# FastAPI reads the JSON body, validates it against `Item`, passes an Item object.
@router.post("/items", summary="Create an item", status_code=status.HTTP_201_CREATED)
def create_item(item: Item) -> dict:
    # Derive the next id from the number of existing items (simple counter).
    new_id = max(IN_MEMORY_ITEMS, default=0) + 1
    IN_MEMORY_ITEMS[new_id] = item
    return {"id": new_id, **item.model_dump()}


# ---- BASIC 5: PUT (replace whole resource) ------------------------------------
@router.put("/items/{item_id}", summary="Replace an item")
def replace_item(item_id: int, item: Item) -> dict:
    if item_id not in IN_MEMORY_ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    IN_MEMORY_ITEMS[item_id] = item       # full replacement
    return {"id": item_id, **item.model_dump()}


# ---- BASIC 6: DELETE -----------------------------------------------------------
@router.delete("/items/{item_id}", summary="Delete an item", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    # 204 No Content => no body returned. Return None (or empty Response).
    if item_id not in IN_MEMORY_ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    IN_MEMORY_ITEMS.pop(item_id)
