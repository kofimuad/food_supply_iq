"""enable postgis extension

This is the bootstrap migration referenced in Story 0.1. On the Railway
PostGIS template (postgis/postgis:17-3.5) the extension files are present but
the extension must still be activated per-database.

Revision ID: 0001_enable_postgis
Revises:
Create Date: 2026-06-25
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_enable_postgis"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS postgis")
