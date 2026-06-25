"""Application settings, loaded from environment / .env."""

from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
