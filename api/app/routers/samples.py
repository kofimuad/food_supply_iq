"""Sample event endpoints (Epic 4, Story 4.1)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user, is_manager
from app.models import Account, Product, Sample, SampleItem, User
from app.schemas.sample import SampleCreate, SampleItemOut, SampleOut

router = APIRouter(tags=["samples"])


async def _account_scoped(account_id: uuid.UUID, db: AsyncSession, user: User) -> Account:
    account = await db.get(Account, account_id)
    if account is None or (not is_manager(user) and account.assigned_rep_id != user.id):
        raise HTTPException(status_code=404, detail="Account not found")
    return account


async def _product_names(db: AsyncSession, ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not ids:
        return {}
    rows = (await db.execute(select(Product.id, Product.name).where(Product.id.in_(ids)))).all()
    return {pid: name for pid, name in rows}


async def _sample_out(db: AsyncSession, sample_id: uuid.UUID) -> SampleOut:
    sample = (
        await db.scalars(
            select(Sample).options(selectinload(Sample.items)).where(Sample.id == sample_id)
        )
    ).one()
    names = await _product_names(db, {it.product_id for it in sample.items})
    return SampleOut(
        id=sample.id,
        account_id=sample.account_id,
        rep_id=sample.rep_id,
        visit_id=sample.visit_id,
        occurred_at=sample.occurred_at,
        items=[
            SampleItemOut(
                product_id=it.product_id,
                product_name=names.get(it.product_id, "—"),
                quantity=it.quantity,
            )
            for it in sample.items
        ],
    )


@router.post(
    "/accounts/{account_id}/samples", response_model=SampleOut, status_code=status.HTTP_201_CREATED
)
async def record_sample(
    account_id: uuid.UUID,
    body: SampleCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SampleOut:
    await _account_scoped(account_id, db, user)

    product_ids = {it.product_id for it in body.items}
    found = await _product_names(db, product_ids)
    missing = product_ids - found.keys()
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Unknown product(s): {sorted(map(str, missing))}"
        )

    sample = Sample(account_id=account_id, rep_id=user.id, visit_id=body.visit_id)
    if body.occurred_at is not None:
        sample.occurred_at = body.occurred_at
    sample.items = [
        SampleItem(product_id=it.product_id, quantity=it.quantity) for it in body.items
    ]
    db.add(sample)
    await db.commit()
    return await _sample_out(db, sample.id)


@router.get("/accounts/{account_id}/samples", response_model=list[SampleOut])
async def list_samples(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[SampleOut]:
    await _account_scoped(account_id, db, user)
    rows = (
        await db.scalars(
            select(Sample)
            .where(Sample.account_id == account_id)
            .order_by(Sample.occurred_at.desc())
            .limit(limit)
        )
    ).all()
    return [await _sample_out(db, s.id) for s in rows]
