"""arq background worker.

Powers repeat-order metrics, funnel rollups, follow-up generation, and scheduled
imports (Epics 4, 6, 8).

Run with:  arq app.worker.WorkerSettings
"""

from arq import cron
from arq.connections import RedisSettings

from app.config import get_settings
from app.db import SessionLocal
from app.services.metrics import recompute_all_order_metrics

settings = get_settings()


async def ping(ctx: dict) -> str:
    """Stub task — proves the worker can pick up jobs from Redis."""
    return "pong"


async def recompute_repeat_metrics(ctx: dict) -> int:
    """Nightly recompute of every account's repeat-order metrics (Story 4.3)."""
    async with SessionLocal() as db:
        return await recompute_all_order_metrics(db)


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


class WorkerSettings:
    functions = [ping, recompute_repeat_metrics]
    # Nightly at 02:00 UTC.
    cron_jobs = [cron(recompute_repeat_metrics, hour=2, minute=0)]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
