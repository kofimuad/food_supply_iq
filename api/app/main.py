"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.routers import accounts, auth, contacts, products, visits

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup / shutdown hooks live here as the app grows (warm caches, etc.).
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(contacts.router)
app.include_router(products.router)
app.include_router(visits.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe — confirms the API process is up."""
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/db", tags=["meta"])
async def health_db() -> dict[str, str]:
    """Readiness probe — confirms Postgres + PostGIS are reachable."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT PostGIS_Version()"))
        postgis_version = result.scalar_one()
    return {"status": "ok", "postgis": str(postgis_version)}
