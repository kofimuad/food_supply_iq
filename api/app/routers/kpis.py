"""Manager KPI dashboard (Epic 6, Story 6.1)."""

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_manager
from app.models import Account, KpiTarget, Order, Sample, User, Visit
from app.models.enums import OrderType
from app.schemas.kpi import KpiMetric, KpiResponse, TargetsOut, TargetsUpdate

router = APIRouter(prefix="/kpis", tags=["kpis"])

# (key, label, date column, aggregate, rep column, extra filters)
_SPECS = [
    ("new_accounts", "New accounts", Account.created_at, func.count(), Account.assigned_rep_id, []),
    ("visits", "Visits", Visit.occurred_at, func.count(), Visit.rep_id, []),
    ("samples", "Samples", Sample.occurred_at, func.count(), Sample.rep_id, []),
    (
        "trial_orders", "Trial orders", Order.occurred_at, func.count(), Order.rep_id,
        [Order.order_type == OrderType.trial],
    ),
    (
        "repeat_orders", "Repeat orders", Order.occurred_at, func.count(), Order.rep_id,
        [Order.order_type == OrderType.repeat],
    ),
    (
        "revenue", "Revenue", Order.occurred_at, func.coalesce(func.sum(Order.total_value), 0),
        Order.rep_id, [],
    ),
]


async def _load_targets(db: AsyncSession) -> dict[str, float]:
    rows = (await db.scalars(select(KpiTarget))).all()
    return {t.metric: float(t.target_value) for t in rows}


@router.get("", response_model=KpiResponse)
async def kpis(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
    rep_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> KpiResponse:
    now = datetime.now(UTC)
    start = date_from or (now - timedelta(days=30))
    end = date_to or now
    targets = await _load_targets(db)

    days: list[date] = []
    d = start.date()
    while d <= end.date():
        days.append(d)
        d += timedelta(days=1)

    metrics: list[KpiMetric] = []
    for key, label, date_col, agg, rep_col, extra in _SPECS:
        filters = [date_col >= start, date_col <= end, *extra]
        if rep_id is not None:
            filters.append(rep_col == rep_id)
        rows = (
            await db.execute(
                select(cast(date_col, Date).label("d"), agg.label("v"))
                .where(*filters)
                .group_by("d")
            )
        ).all()
        series = {r.d: float(r.v) for r in rows}
        spark = [series.get(day, 0.0) for day in days]
        metrics.append(
            KpiMetric(
                key=key,
                label=label,
                value=round(sum(spark), 2),
                target=targets.get(key),
                spark=spark,
            )
        )

    return KpiResponse(date_from=start, date_to=end, metrics=metrics)


@router.get("/targets", response_model=TargetsOut)
async def get_targets(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> TargetsOut:
    return TargetsOut(targets=await _load_targets(db))


@router.put("/targets", response_model=TargetsOut)
async def set_targets(
    body: TargetsUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> TargetsOut:
    existing = {t.metric: t for t in (await db.scalars(select(KpiTarget))).all()}
    for metric, value in body.targets.items():
        if metric in existing:
            existing[metric].target_value = value
        else:
            db.add(KpiTarget(metric=metric, target_value=value))
    await db.commit()
    return TargetsOut(targets=await _load_targets(db))
