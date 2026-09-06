# =============================================================================
# models/task.py  --  the Task ORM model
# =============================================================================

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)   # required (nullable=False)
    description = Column(Text, nullable=True)     # optional, long text
    done = Column(Boolean, default=False)
    priority = Column(Integer, default=1)         # 1..5 to show ordering / filters

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # A user owns many tasks -> each task references the owning user's id.
    # ForeignKey("users.id") = DB foreign key constraint (referential integrity).
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship back to the User model (the other side of User.tasks).
    # back_populates="tasks" keeps the two sides in sync.
    owner = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} done={self.done} title={self.title!r}>"
