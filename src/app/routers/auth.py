# =============================================================================
# routers/auth.py  --  LEVEL 3 (ADVANCED) : JWT authentication endpoints
# =============================================================================
# CONCEPTS:
#   * OAuth2PasswordRequestForm: FastAPI's built-in form for login
#     (expects `username` + `password` form fields, NOT JSON).
#   * OAuth2 + JWT stateless auth flow:
#       1. Client POSTs /auth/login with (username=email, password)
#       2. We verify credentials, make a signed JWT, return {access_token}
#       3. Client sends `Authorization: Bearer <token>` on protected routes
#       4. Server decodes+verifies the token (see api/deps.py) -> identity
#   * Token expiry: the JWT carries exp; after it passes the token is useless,
#     forcing re-login. Stateless = no server-side session storage (scales).

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import DbDep
from app.core.security import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services.crud import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Register a new user ------------------------------------------------------
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbDep) -> UserRead:
    """Create an account. Returns the public user info (no password).
       Raises 409 if the email already exists (idempotency / duplicate check)."""
    if UserService.get_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return UserService.create(db, data)


# --- Login (OAuth2 password flow) ---------------------------------------------
@router.post("/login", response_model=Token)
def login(db: DbDep, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Exchange valid credentials for a signed JWT.
       OAuth2PasswordRequestForm reads `grant_type` + `username` + `password`
       form fields. We accept the user's email in the `username` field."""
    user = UserService.authenticate(db, form_data.username, form_data.password)
    if not user:
        # Deliberately vague message: do NOT reveal whether the email exists.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # On success, mint a token embedding the user id as the subject.
    return Token(access_token=create_access_token(user.id))
