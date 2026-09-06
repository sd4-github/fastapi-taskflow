# =============================================================================
# models/__init__.py  --  exports all models so `from app import models` works
# =============================================================================

from app.models.task import Task
from app.models.user import User

__all__ = ["Task", "User"]
