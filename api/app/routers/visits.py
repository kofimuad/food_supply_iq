"""Field visit endpoints (Epic 3, Story 3.1)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, is_manager
from app.models import Account, User, Visit
from app.schemas.visit import VisitCreate, VisitOut
from app.utils.geo import to_point

router = APIRouter(tags=["visits"])

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")


async def _account_scoped(account_id: uuid.UUID, db: AsyncSession, user: User) -> Account:
    account = await db.get(Account, account_id)
    if account is None or (not is_manager(user) and account.assigned_rep_id != user.id):
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post(
    "/accounts/{account_id}/visits",
    response_model=VisitOut,
    status_code=status.HTTP_201_CREATED,
)
async def log_visit(
    account_id: uuid.UUID,
    body: VisitCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> VisitOut:
    """Check in / log a visit. Attributed to the signed-in rep."""
    await _account_scoped(account_id, db, user)
    has_coords = body.lat is not None and body.lng is not None
    visit = Visit(
        account_id=account_id,
        rep_id=user.id,
        notes=body.notes,
        outcome=body.outcome,
        location=to_point(body.lng, body.lat) if has_coords else None,
    )
    if body.occurred_at is not None:
        visit.occurred_at = body.occurred_at
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return VisitOut.from_model(visit)


@router.get("/accounts/{account_id}/visits", response_model=list[VisitOut])
async def list_visits(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[VisitOut]:
    await _account_scoped(account_id, db, user)
    rows = (
        await db.scalars(
            select(Visit)
            .where(Visit.account_id == account_id)
            .order_by(Visit.occurred_at.desc())
            .limit(limit)
        )
    ).all()
    return [VisitOut.from_model(v) for v in rows]


@router.get("/visits/{visit_id}", response_model=VisitOut)
async def get_visit(
    visit_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> VisitOut:
    visit = await db.get(Visit, visit_id)
    if visit is None:
        raise _NOT_FOUND
    # Scope through the owning account.
    await _account_scoped(visit.account_id, db, user)
    return VisitOut.from_model(visit)
