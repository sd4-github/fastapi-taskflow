# =============================================================================
# api/deps.py  --  FastAPI dependencies (auth / db injection)
# =============================================================================
# FastAPI *dependency injection* is a core interview topic:
#   * Endpoints can declare dependencies in their signature, e.g. `db: Session
#     = Depends(get_db)`. FastAPI resolves them, calls them, and passes the
#     result. This removes boilerplate (no manual session/token handling).
#   * Dependencies can be reused and COMPOSED: get_current_user itself depends
#     on get_db + the OAuth2 scheme, then returns the authenticated User.
#
#   OAuth2PasswordBearer(tokenUrl="/auth/login"):
#     - tells FastAPI "this API protects routes with a bearer token"
#     - reads the `Authorization: Bearer <token>` header automatically
#     - if token missing => auto 401
#     - Some docs call this "the toughest part of FastAPI" because it uses
#       OAuth2 password flow terminology; but here it's just a header extractor.
#
#   security_scopes / OAuth2 scopes: a way to define PERMISSIONS a token grants.
#   We keep it simple but mention it below.

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# tokenUrl tells the interactive /docs page where to POST credentials for the
# "Authorize" button. auto_error=True => missing token raises 401 automatically.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Type aliases keep signatures readable (Python 3.9+ union syntax).
DbDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


# --- Optional: an authenticated user, or None ---------------------------------
def get_current_user(
    db: DbDep,
    token: TokenDep,
) -> User | None:
    """Resolve the bearer token into a User, or None if absent/invalid.
       Used on routes that are accessible both logged-in and anonymously."""
    if not token:
        return None
    return get_user_or_raise(db, token)


# --- Required: an authenticated user, else 401 ---------------------------------
def get_current_user_required(
    db: DbDep,
    token: TokenDep,
) -> User:
    """Like above but REQUIRES a valid token (raises 401 if not)."""
    user = get_current_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# --- Required superuser (admin-only routes) -----------------------------------
def get_current_superuser(current_user: Annotated[User, Depends(get_current_user_required)]) -> User:
    """Enforces role/permission: only superusers pass. Raises 403 otherwise."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# --- shared internal helper ----------------------------------------------------
def get_user_or_raise(db: Session, token: str) -> User:
    """Decode + validate token, load the User row, or raise 401."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)        # raises JWTError if bad/expired
    except JWTError:
        raise credentials_exc

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exc

    user = db.get(User, int(user_id))               # fetch User by PK
    if user is None or not user.is_active:
        raise credentials_exc
    return user


# Convenience aliases used by routers for clean annotations.
CurrentUser = Annotated[User, Depends(get_current_user_required)]
CurrentUserOptional = Annotated[User, Depends(get_current_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]
