# =============================================================================
# routers/tasks.py  --  LEVEL 2-3 (INTERMEDIATE->ADVANCED) : authenticated CRUD
# =============================================================================
# Builds on basic.py but now: uses the DB (Postgres via SQLAlchemy), the DI for
# sessions, JWT auth, pagination, and response_model validation.
#
# Key advanced patterns shown here:
#   * response_model=TaskRead  : FastAPI validates+serializes the response and
#     builds the OpenAPI schema automatically. Returned dicts get validated.
#   * Depends auth: Annotated[User, Depends(CurrentUser)] injects the logged-in
#     user object into the endpoint (see api/deps.py).
#   * HTTPException with proper status codes (201/404/403...).
#   * Row-level ownership: every query is scoped by owner_id so users can only
#     touch their own tasks.

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.crud import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


# --- CREATE ---------------------------------------------------------------
@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: DbDep, current_user: CurrentUser) -> TaskRead:
    """Create a new task owned by the authenticated user.
       `current_user` is injected by the auth dependency."""
    task = TaskService.create(db, owner_id=current_user.id, data=data)
    return TaskRead.model_validate(task)   # convert ORM -> schema


# --- LIST (paginated + filterable) -----------------------------------------
@router.get("", response_model=dict)
def list_tasks(
    db: DbDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    done: bool | None = None,
    priority: int | None = None,
) -> dict:
    """Return the user's tasks with optional filters and paging metadata.
       Note: `limit=20` — always cap list endpoints to avoid huge payloads."""
    tasks = TaskService.list(db, current_user.id, skip, limit, done, priority)
    total = TaskService.count(db, current_user.id)
    # return dict with items + pagination metadata (industry-standard shape)
    return {
        "items": [TaskRead.model_validate(t) for t in tasks],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# --- READ ONE --------------------------------------------------------------
@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: DbDep, current_user: CurrentUser) -> TaskRead:
    task = TaskService.get(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


# --- UPDATE (PATCH semantics) ----------------------------------------------
@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DbDep,
    current_user: CurrentUser,
) -> TaskRead:
    task = TaskService.get(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task = TaskService.update(db, task, data)
    return TaskRead.model_validate(task)


# --- DELETE ----------------------------------------------------------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbDep, current_user: CurrentUser) -> None:
    task = TaskService.get(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    TaskService.delete(db, task)
