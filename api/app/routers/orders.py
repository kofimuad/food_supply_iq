"""Order endpoints — trial + repeat (Epic 4, Stories 4.2–4.3)."""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user, is_manager
from app.models import Account, Order, OrderItem, Product, User
from app.schemas.order import OrderCreate, OrderItemOut, OrderOut

router = APIRouter(tags=["orders"])


async def _account_scoped(account_id: uuid.UUID, db: AsyncSession, user: User) -> Account:
    account = await db.get(Account, account_id)
    if account is None or (not is_manager(user) and account.assigned_rep_id != user.id):
        raise HTTPException(status_code=404, detail="Account not found")
    return account


async def _order_out(db: AsyncSession, order_id: uuid.UUID) -> OrderOut:
    order = (
        await db.scalars(
            select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        )
    ).one()
    ids = {it.product_id for it in order.items}
    names = dict(
        (await db.execute(select(Product.id, Product.name).where(Product.id.in_(ids)))).all()
    )
    return OrderOut(
        id=order.id,
        account_id=order.account_id,
        rep_id=order.rep_id,
        order_type=order.order_type,
        sample_id=order.sample_id,
        visit_id=order.visit_id,
        occurred_at=order.occurred_at,
        total_value=float(order.total_value),
        currency=order.currency,
        items=[
            OrderItemOut(
                product_id=it.product_id,
                product_name=names.get(it.product_id, "—"),
                quantity=it.quantity,
                unit_price=float(it.unit_price),
            )
            for it in order.items
        ],
    )


@router.post(
    "/accounts/{account_id}/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED
)
async def create_order(
    account_id: uuid.UUID,
    body: OrderCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> OrderOut:
    await _account_scoped(account_id, db, user)

    ids = {it.product_id for it in body.items}
    products = {
        p.id: p for p in (await db.scalars(select(Product).where(Product.id.in_(ids)))).all()
    }
    missing = ids - products.keys()
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Unknown product(s): {sorted(map(str, missing))}"
        )

    # Snapshot unit prices from the catalog so later price edits don't rewrite history.
    order = Order(
        account_id=account_id,
        rep_id=user.id,
        order_type=body.order_type,
        sample_id=body.sample_id,
        visit_id=body.visit_id,
        currency=next((products[i].currency for i in ids), "USD"),
    )
    if body.occurred_at is not None:
        order.occurred_at = body.occurred_at

    total = Decimal("0")
    items = []
    for it in body.items:
        price = products[it.product_id].price or Decimal("0")
        items.append(
            OrderItem(product_id=it.product_id, quantity=it.quantity, unit_price=price)
        )
        total += price * it.quantity
    order.items = items
    order.total_value = total

    db.add(order)
    await db.commit()
    return await _order_out(db, order.id)


@router.get("/accounts/{account_id}/orders", response_model=list[OrderOut])
async def list_orders(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[OrderOut]:
    await _account_scoped(account_id, db, user)
    rows = (
        await db.scalars(
            select(Order)
            .where(Order.account_id == account_id)
            .order_by(Order.occurred_at.desc())
            .limit(limit)
        )
    ).all()
    return [await _order_out(db, o.id) for o in rows]
