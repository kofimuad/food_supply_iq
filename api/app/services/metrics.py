"""Derived account order metrics (Story 4.3).

Recomputed immediately when an order is created (responsiveness) and by a nightly
arq job (consistency). "Repeating" = the account has placed >= 2 orders.
"""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account, Order
from app.models.enums import OrderType


async def recompute_account_order_metrics(db: AsyncSession, account_id: uuid.UUID) -> None:
    """Update one account's repeat metrics. Does not commit (caller commits)."""
    total = await db.scalar(
        select(func.count()).select_from(Order).where(Order.account_id == account_id)
    )
    repeats = await db.scalar(
        select(func.count())
        .select_from(Order)
        .where(Order.account_id == account_id, Order.order_type == OrderType.repeat)
    )
    last = await db.scalar(
        select(func.max(Order.occurred_at)).where(Order.account_id == account_id)
    )
    await db.execute(
        update(Account)
        .where(Account.id == account_id)
        .values(
            is_repeating=(total or 0) >= 2,
            repeat_order_count=repeats or 0,
            last_order_at=last,
        )
    )


async def recompute_all_order_metrics(db: AsyncSession) -> int:
    """Recompute metrics for every account that has orders. Returns the count."""
    account_ids = (await db.scalars(select(Order.account_id).distinct())).all()
    for account_id in account_ids:
        await recompute_account_order_metrics(db, account_id)
    await db.commit()
    return len(account_ids)
