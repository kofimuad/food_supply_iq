"""Sample → Trial → Repeat funnel (Epic 4, Story 4.4). Manager-only."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_manager
from app.models import Account, Order, OrderItem, Sample, SampleItem, User
from app.models.enums import OrderType
from app.schemas.account import AccountOut
from app.schemas.funnel import FunnelStage

router = APIRouter(tags=["funnel"])


async def _sampled_ids(
    db, rep_id, date_from, date_to, product_id
) -> set[uuid.UUID]:
    stmt = select(Sample.account_id)
    if product_id is not None:
        stmt = stmt.join(SampleItem, SampleItem.sample_id == Sample.id).where(
            SampleItem.product_id == product_id
        )
    if rep_id is not None:
        stmt = stmt.where(Sample.rep_id == rep_id)
    if date_from is not None:
        stmt = stmt.where(Sample.occurred_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(Sample.occurred_at <= date_to)
    return set((await db.scalars(stmt.distinct())).all())


async def _order_ids(
    db, order_type, rep_id, date_from, date_to, product_id
) -> set[uuid.UUID]:
    stmt = select(Order.account_id).where(Order.order_type == order_type)
    if product_id is not None:
        stmt = stmt.join(OrderItem, OrderItem.order_id == Order.id).where(
            OrderItem.product_id == product_id
        )
    if rep_id is not None:
        stmt = stmt.where(Order.rep_id == rep_id)
    if date_from is not None:
        stmt = stmt.where(Order.occurred_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(Order.occurred_at <= date_to)
    return set((await db.scalars(stmt.distinct())).all())


async def _stage_sets(db, rep_id, date_from, date_to, product_id):
    sampled = await _sampled_ids(db, rep_id, date_from, date_to, product_id)
    trial = await _order_ids(db, OrderType.trial, rep_id, date_from, date_to, product_id)
    repeat = await _order_ids(db, OrderType.repeat, rep_id, date_from, date_to, product_id)
    return {"sampled": sampled, "trial": trial, "repeat": repeat}


def _pct(num: int, denom: int) -> float | None:
    return round(num / denom * 100, 1) if denom else None


@router.get("/funnel", response_model=list[FunnelStage])
async def funnel(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
    rep_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[FunnelStage]:
    sets = await _stage_sets(db, rep_id, date_from, date_to, product_id)
    n_sampled, n_trial, n_repeat = (
        len(sets["sampled"]),
        len(sets["trial"]),
        len(sets["repeat"]),
    )
    return [
        FunnelStage(key="sampled", label="Sampled", count=n_sampled, conversion_from_prev=None),
        FunnelStage(
            key="trial", label="Trial", count=n_trial, conversion_from_prev=_pct(n_trial, n_sampled)
        ),
        FunnelStage(
            key="repeat",
            label="Repeat",
            count=n_repeat,
            conversion_from_prev=_pct(n_repeat, n_trial),
        ),
    ]


@router.get("/funnel/accounts", response_model=list[AccountOut])
async def funnel_accounts(
    stage: str = Query(pattern="^(sampled|trial|repeat)$"),
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
    rep_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[AccountOut]:
    sets = await _stage_sets(db, rep_id, date_from, date_to, product_id)
    ids = sets.get(stage, set())
    if not ids:
        return []
    rows = (
        await db.scalars(select(Account).where(Account.id.in_(ids)).order_by(Account.name))
    ).all()
    return [AccountOut.from_model(a) for a in rows]
