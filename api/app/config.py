"""Application settings, loaded from environment / .env."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FoodSupply IQ API"
    environment: str = "development"
    debug: bool = True

    # Postgres + PostGIS. asyncpg driver for the app, psycopg/sync URL for Alembic.
    database_url: str = "postgresql+asyncpg://fsiq:fsiq@localhost:5440/fsiq"

    # Redis powers arq background jobs (funnel rollups, scoring, follow-ups).
    redis_url: str = "redis://localhost:6380/0"

    # CORS origins for the web dashboard / mobile dev client.
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    # --- Auth / JWT (Story 0.3) ---
    jwt_secret: str = "dev-insecure-change-me-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    # Access tokens are generous so a rep can stay productive offline for a full
    # field day without a refresh; refresh tokens are long-lived for the same reason.
    access_token_expire_minutes: int = 60 * 12  # 12 hours
    refresh_token_expire_days: int = 90

    @field_validator("database_url")
    @classmethod
    def _ensure_asyncpg_driver(cls, v: str) -> str:
        # Railway's managed Postgres hands out a `postgresql://` (or legacy
        # `postgres://`) URL; SQLAlchemy's async engine needs the asyncpg driver.
        if v.startswith("postgresql+"):
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
