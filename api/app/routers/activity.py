"""Cross-team activity feed for managers (Epic 3, Story 3.2)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_manager
from app.models import Account, Order, Sample, User, Visit
from app.schemas.activity import ActivityEvent, ActivityFeed

router = APIRouter(tags=["activity"])


@router.get("/activity", response_model=ActivityFeed)
async def activity_feed(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
    rep_id: uuid.UUID | None = Query(default=None),
    before: datetime | None = Query(default=None, description="Cursor: only events before this"),
    limit: int = Query(default=30, ge=1, le=100),
) -> ActivityFeed:
    events: list[ActivityEvent] = []

    def scoped(stmt, model):
        if rep_id is not None:
            stmt = stmt.where(model.rep_id == rep_id)
        if before is not None:
            stmt = stmt.where(model.occurred_at < before)
        return stmt.order_by(model.occurred_at.desc()).limit(limit)

    # Visits
    for v, name in (
        await db.execute(scoped(select(Visit, Account.name).join(Account), Visit))
    ).all():
        events.append(
            ActivityEvent(
                type="visit",
                id=v.id,
                account_id=v.account_id,
                account_name=name,
                rep_id=v.rep_id,
                occurred_at=v.occurred_at,
                detail=v.outcome.value if v.outcome else "visit logged",
            )
        )

    # Samples
    for s, name in (
        await db.execute(scoped(select(Sample, Account.name).join(Account), Sample))
    ).all():
        events.append(
            ActivityEvent(
                type="sample",
                id=s.id,
                account_id=s.account_id,
                account_name=name,
                rep_id=s.rep_id,
                occurred_at=s.occurred_at,
                detail="sample given",
            )
        )

    # Orders
    for o, name in (
        await db.execute(scoped(select(Order, Account.name).join(Account), Order))
    ).all():
        events.append(
            ActivityEvent(
                type="order",
                id=o.id,
                account_id=o.account_id,
                account_name=name,
                rep_id=o.rep_id,
                occurred_at=o.occurred_at,
                detail=f"{o.order_type.value} order · {o.total_value} {o.currency}",
            )
        )

    events.sort(key=lambda e: e.occurred_at, reverse=True)
    page = events[:limit]
    next_cursor = page[-1].occurred_at if len(page) == limit else None
    return ActivityFeed(items=page, next_cursor=next_cursor)
