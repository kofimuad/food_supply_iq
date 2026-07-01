"""Configurable KPI targets (Epic 6, Story 6.1)."""

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class KpiTarget(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "kpi_targets"

    # One target per metric key (e.g. "visits", "revenue").
    metric: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
