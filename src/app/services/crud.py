# =============================================================================
# services/crud.py  --  LEVEL 2-3 : Business logic / DB access layer
# =============================================================================
# WHY A SERVICE LAYER? (industry-standard architecture / interview question)
#   Routers should be THIN: they only handle HTTP in/out. All real logic +
#   database access lives in a separate service layer. Benefits:
#     1. Testable  : you can test service functions without HTTP.
#     2. Reusable  : multiple routers/endpoints share the same service.
#     3. Maintainable: business rules live in one place.
#   This is the classic "layered architecture" (router -> service -> repository/ORM).
#
# SQLAlchemy session usage (interview):
#   * We receive `db: Session` (the request-scoped dependency) and run queries.
#   * db.add(obj)      : queue an object for insertion.
#   * db.commit()      : flush + send the transaction to Postgres (persist).
#   * db.refresh(obj)  : reload obj from DB to get server-generated fields
#                        (e.g. the auto-incremented id or timestamps).
#   * db.query(Model)  : build a query (SELECT).
#     .filter(...)     : WHERE clause
#     .offset/.limit   : pagination (skip/take)
#     .all() / .first(): execute and fetch results.

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.user import UserCreate


class UserService:
    """Operations on the User model."""

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        # .filter(User.email == email).first()  -> WHERE email = ?  LIMIT 1
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def create(db: Session, data: UserCreate) -> User:
        """Hash the password, persist the user, commit, and refresh."""
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),  # NEVER store raw
        )
        db.add(user)
        db.commit()
        db.refresh(user)   # pull server-generated id/created_at back
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        """Verify credentials; returns the User or None on bad email/password."""
        user = UserService.get_by_email(db, email)
        if user is None or not user.verify_password(password):
            return None
        return user


class TaskService:
    """Operations on the Task model, scoped to a specific owner (user)."""

    # -- Create -----------------------------------------------------------
    @staticmethod
    def create(db: Session, owner_id: int, data: TaskCreate) -> Task:
        task = Task(owner_id=owner_id, **data.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    # -- Read (with pagination + filtering) -------------------------------
    @staticmethod
    def list(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 20,
        done: bool | None = None,
        priority: int | None = None,
    ) -> list[Task]:
        """Return the owner's tasks, optionally filtered by done/priority.
           Demonstrates building a query dynamically + pagination."""
        query = db.query(Task).filter(Task.owner_id == owner_id)
        # Conditional WHERE clauses (only add filter if param provided)
        if done is not None:
            query = query.filter(Task.done == done)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        # Order newest first for predictable pagination, then skip/limit.
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        return query.all()

    @staticmethod
    def count(db: Session, owner_id: int) -> int:
        """Total number of tasks for the owner (for paging metadata)."""
        return db.query(Task).filter(Task.owner_id == owner_id).count()

    @staticmethod
    def get(db: Session, owner_id: int, task_id: int) -> Task | None:
        # IMPORTANT: filter by BOTH id AND owner_id. This enforces that a user
        # can only fetch their OWN task (row-level access control).
        return (
            db.query(Task)
            .filter(Task.id == task_id, Task.owner_id == owner_id)
            .first()
        )

    # -- Update (partial, only touch provided fields) ---------------------
    @staticmethod
    def update(db: Session, task: Task, data: TaskUpdate) -> Task:
        # model_dump(exclude_unset=True) returns ONLY fields the client actually
        # sent. This is the correct PATCH semantic (don't overwrite what wasn't sent).
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(task, field, value)   # setattr = dynamic attribute assignment
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    # -- Delete -------------------------------------------------------------
    @staticmethod
    def delete(db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()
