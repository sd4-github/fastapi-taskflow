# =============================================================================
# schemas/task.py  --  Pydantic schemas for tasks
# =============================================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Shared base: fields common to create & read -----------------------------
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    done: bool = False
    priority: int = Field(default=1, ge=1, le=5)   # ge=1 le=5 -> range [1,5]


# --- Create: what the client MUST send ---------------------------------------
class TaskCreate(TaskBase):
    pass


# --- Update: all optional, so partial updates (PATCH) work -------------------
class TaskUpdate(BaseModel):
    # Optional fields: if omitted, we don't change them (only patch what's sent)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    done: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


# --- Read: what the API returns ----------------------------------------------
class TaskRead(TaskBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
