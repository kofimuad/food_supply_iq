"""Alembic environment — async engine, URL pulled from app settings."""

import asyncio
from logging.config import fileConfig

from alembic import context

# Import models so Alembic autogenerate sees every table on Base.metadata.
from app import models  # noqa: F401
from app.config import get_settings
from app.db import Base
from geoalchemy2 import alembic_helpers
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()


def include_object(obj, name, type_, reflected, compare_to):
    """Keep autogenerate to *our* tables.

    The postgis/postgis image ships the tiger-geocoder and topology schemas on
    the search path, so a naive autogenerate tries to DROP dozens of tables we
    don't own. Ignore any reflected object whose table isn't in our metadata,
    then defer to geoalchemy2 for geography columns / spatial indexes.
    """
    if reflected and type_ == "table" and name not in target_metadata.tables:
        return False
    if reflected and type_ in ("index", "unique_constraint", "foreign_key_constraint", "column"):
        table = getattr(obj, "table", None)
        if table is not None and table.name not in target_metadata.tables:
            return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


def do_run_migrations(connection) -> None:
    # geoalchemy2 helpers teach autogenerate about geography columns + spatial
    # indexes; include_object filters out PostGIS-managed tables.
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        render_item=alembic_helpers.render_item,
        process_revision_directives=alembic_helpers.writer,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(settings.database_url, future=True)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
