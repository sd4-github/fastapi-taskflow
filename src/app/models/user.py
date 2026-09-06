# =============================================================================
# models/user.py  --  the User ORM model
# =============================================================================
# ORM (Object Relational Mapping): each class = a DB table, each attribute =
# a column. SQLAlchemy translates your Python objects into SQL statements.
#
# IMPORTS / CONCEPTS:
#   * Column(...)       : defines a table column
#   * Integer/Boolean/DateTime : SQL column types
#   * relationship(...) : defines how two tables relate (for queries)
#   * Mapped[]          : SQLAlchemy 2.0 "typed" column style instead of Column()
#     We'll use the classic Column() style here for clarity, but mention Mapped.
#
# AUTH: We do NOT store plaintext passwords. We store a bcrypt hash via
#       passlib. Storing hashes protects users if the DB leaks.

from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

# CryptContext bundles config for password hashing.
# schemes=["bcrypt"] -> use bcrypt algorithm. deprecated="auto" keeps it clean.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"            # actual table name in Postgres

    # primary_key=True -> indexed + unique id the DB auto-increments
    id = Column(Integer, primary_key=True, index=True)

    # unique=True -> DB-level constraint: no two users with same email
    # index=True  -> Postgres builds a fast lookup index on this column
    email = Column(String(255), unique=True, index=True, nullable=False)

    # store the BCRYPT HASH, never the raw password
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # auto-set timestamps when a row is created/updated
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # relationship("Task")  -> when you fetch a User, you can access
    #                          user.tasks to get their Tasks (lazy loaded).
    # back_populates="owner" links BOTH sides so Task.owner <-> User.tasks
    # are the "same" relationship for SQLAlchemy.
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    # --- helper methods (no plaintext passwords anywhere) -------------------
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a raw password into a one-way bcrypt digest."""
        return pwd_context.hash(password)

    def verify_password(self, raw_password: str) -> bool:
        """Check a candidate password against the stored hash.
           Returns True/False. Never compare plaintext strings."""
        return pwd_context.verify(raw_password, self.hashed_password)

    def __repr__(self) -> str:
        # __repr__ defines how Python prints the object in logs/REPL.
        return f"<User id={self.id} email={self.email}>"
