"""KPI dashboard schemas (Epic 6, Story 6.1)."""

from datetime import datetime

from pydantic import BaseModel


class KpiMetric(BaseModel):
    key: str
    label: str
    value: float
    target: float | None
    spark: list[float]  # daily series across the window, for a sparkline


class KpiResponse(BaseModel):
    date_from: datetime
    date_to: datetime
    metrics: list[KpiMetric]


class TargetsUpdate(BaseModel):
    targets: dict[str, float]


class TargetsOut(BaseModel):
    targets: dict[str, float]
