# =============================================================================
# core/config.py  --  Application configuration
# =============================================================================
# WHY Pydantic Settings?
#   In real apps you NEVER hardcode secrets/URLs. You read them from:
#     1. Environment variables (set by Docker, CI, prod servers)
#     2. A .env file (for local dev, git-ignored)
#   pydantic-settings loads BOTH, validates types, and gives you typed
#   `.env`-aware attributes like `settings.DATABASE_URL`.
#
#   `BaseSettings` + a `model_config` with env_file=".env" is the idiomatic
#   FastAPI way. It also auto-casts: a field typed `int` from env "8080"
#   becomes an actual int.

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# We subclass BaseSettings. Each class attribute = a config field.
# Field name maps to an env var of the same name (case-insensitive) by default.
class Settings(BaseSettings):
    # --- App core -----------------------------------------------------------
    APP_NAME: str = "TaskFlow API"      # Display name for docs
    APP_VERSION: str = "1.0.0"          # Version shown in /docs
    DEBUG: bool = False                 # Debug mode (turns on verbose errors)

    # --- Database -----------------------------------------------------------
    # SQLAlchemy connection URL. Points at our local Postgres 'taskflow' DB.
    # sqlalchemy://driver://user:pass@host:port/dbname
    DATABASE_URL: str = "postgresql+psycopg2://taskflow:taskflow@127.0.0.1:5432/taskflow"

    # --- Redis ---------------------------------------------------------------
    # Used for caching & rate limiting. Local Docker redis on default port.
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # --- Security / Auth -----------------------------------------------------
    # Secret used to SIGN JWT tokens. NEVER commit real secrets.
    SECRET_KEY: str = "change-me-in-production-super-secret"
    ALGORITHM: str = "HS256"            # JWT signing algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # token lifetime

    # --- Rate limiting ------------------------------------------------------
    RATE_LIMIT_REQUESTS: int = 5        # max requests...
    RATE_LIMIT_WINDOW: int = 60         # ...per this many seconds

    # pydantic-settings v2 config:
    #   env_file=".env" -> also read values from a .env file
    #   extra="ignore"  -> ignore unknown vars so reusing shell env is safe
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# `lru_cache` makes this a lazy singleton: the settings are read ONCE
# and cached. Calling get_settings() repeatedly returns the same object,
# so env/`.env` is only parsed a single time at first call.
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# A module-level convenience instance for most code paths.
# (get_settings() is still useful for dependency-injected contexts/tests.)
settings = get_settings()
