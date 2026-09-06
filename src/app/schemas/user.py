# =============================================================================
# schemas/user.py  --  Pydantic schemas for users
# =============================================================================
# Pydantic = FastAPI's data-validation layer. Schemas define the SHAPE of data
# moving in/out of the API and AUTO-VALIDATE it.
#
# Key concepts (interview):
#   * BaseModel subclasses auto-parse + validate the input into typed fields.
#   * Field(...) adds constraints: min_length, max_length, gt (greater than).
#   * EmailStr requires the email-validator package; catches bad emails.
#   * ConfigDict(from_attributes=True) lets Pydantic read from ORM objects
#     (model_dump / validation from SQLAlchemy rows) instead of only dicts.
#   * We split schemas: a CREATE schema vs a READ schema. This is important so
#     we never accidentally expose hashed_password.

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Input schema for creating a user --------------------------------------
class UserCreate(BaseModel):
    # Field(min_length=3, max_length=50) validates length on input.
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


# --- Output schema: what a client sees about a user ------------------------
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool

    # Tell Pydantic it can populate these fields from an ORM object
    # (e.g. a SQLAlchemy User row) using its attribute access, not just dicts.
    model_config = ConfigDict(from_attributes=True)
