# =============================================================================
# schemas/token.py  --  schemas for JWT authentication responses
# =============================================================================

from pydantic import BaseModel


# What the login endpoint returns: the access token + its type.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# The decoded payload inside a JWT (used after verifying a request's token).
class TokenPayload(BaseModel):
    sub: str         # "subject" = usually the user id, per JWT spec
    exp: int         # expiry timestamp (unix seconds) added by jose
