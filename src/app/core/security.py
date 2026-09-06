# =============================================================================
# core/security.py  --  JWT creation/verification + password hashing
# =============================================================================
# JWT (JSON Web Token) interview essentials:
#   * A JWT is a signed, self-contained token: header.payload.signature
#   * Header : meta (alg = algorithm used, e.g. HS256)
#   * Payload: claims (who it is + expiry). We store "sub" (subject = user id).
#   * Signature: HMAC SHA-256 of (header + payload) using our SECRET_KEY.
#   * Because the signature is secret-key-derived, clients cannot forge tokens.
#   * We DON'T store tokens on the server = stateless auth. Great for scaling.
#
#   `jwt.encode(payload, key, algorithm)`   -> produces a token string
#   `jwt.decode(token, key, algorithms=[])` -> verifies signature + returns payload
#   A token also carries "exp" = expiry; jose rejects it after that time.

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt is the default, battle-tested password hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Return a bcrypt hash of the password (never stored in plaintext)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(subject: str | int) -> str:
    """Build and sign an access token for a given user id (subject)."""
    # The time the token is created, as a timezone-aware UTC instant.
    now = datetime.now(timezone.utc)
    # payload carries the standard "sub" + "exp" claims.
    payload = {
        "sub": str(subject),                                   # user id
        "iat": now,                                            # issued-at
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    # jwt.encode signs payload with our secret, returning a token string.
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify the token's signature + expiry and return its claims (payload).
       Raises JWTError if the token is invalid OR expired."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
