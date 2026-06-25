"""arq background worker.

Powers funnel rollups, repeat-order intelligence, follow-up task generation,
and scheduled imports (Epics 4, 6, 8). For now it holds a stub task so the
worker boots and the Redis wiring is verifiable.

Run with:  arq app.worker.WorkerSettings
"""

from arq.connections import RedisSettings

from app.config import get_settings

settings = get_settings()


async def ping(ctx: dict) -> str:
    """Stub task — proves the worker can pick up jobs from Redis."""
    return "pong"


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


class WorkerSettings:
    functions = [ping]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
