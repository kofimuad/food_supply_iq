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
    # NOTE: list the WEB frontend origin(s) here, with NO trailing slash. Override
    # in production via the CORS_ORIGINS env var.
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "https://web-production-a328bf.up.railway.app",
        "https://api-production-19cc.up.railway.app",
    ]

    # --- Auth / JWT (Story 0.3) ---
    jwt_secret: str = "dev-insecure-change-me-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    # Access tokens are generous so a rep can stay productive offline for a full
    # field day without a refresh; refresh tokens are long-lived for the same reason.
    access_token_expire_minutes: int = 60 * 12  # 12 hours
    refresh_token_expire_days: int = 90

    # Mapbox token for geocoding addresses (Epic 1) / maps + routing (Epics 5, 10).
    # If unset, account geocoding is skipped gracefully.
    mapbox_token: str | None = None

    # --- S3-compatible storage for visit photos (Epic 3, Story 3.3) ---
    # Defaults target the local MinIO from docker-compose. In prod set these to
    # Cloudflare R2 or Railway-MinIO.
    s3_endpoint: str | None = "http://localhost:9000"
    s3_access_key: str | None = "minioadmin"
    s3_secret_key: str | None = "minioadmin"
    s3_bucket: str = "fsiq-media"
    s3_region: str = "us-east-1"
    # Best-effort bucket creation (handy for dev/MinIO; harmless if it lacks perms).
    s3_auto_create_bucket: bool = True

    @property
    def storage_enabled(self) -> bool:
        return bool(self.s3_endpoint and self.s3_access_key and self.s3_secret_key)

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
