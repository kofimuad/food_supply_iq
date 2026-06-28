"""Account endpoints (Epic 1, Stories 1.1–1.2)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, is_manager, require_manager
from app.models import Account, User
from app.models.enums import AccountCategory, AccountStatus
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate
from app.schemas.common import Page
from app.services.geocoding import geocode
from app.utils.geo import to_point

router = APIRouter(prefix="/accounts", tags=["accounts"])

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


async def _resolve_point(
    lat: float | None, lng: float | None, address: str | None
) -> WKTElement | None:
    """Prefer explicit coordinates; otherwise geocode the address (best-effort)."""
    if lat is not None and lng is not None:
        return to_point(lng, lat)
    if address:
        coords = await geocode(address)
        if coords:
            return to_point(coords[0], coords[1])
    return None


async def _get_scoped(account_id: uuid.UUID, db: AsyncSession, user: User) -> Account:
    """Load an account, 404ing if a rep tries to reach one that isn't theirs."""
    account = await db.get(Account, account_id)
    if account is None:
        raise _NOT_FOUND
    if not is_manager(user) and account.assigned_rep_id != user.id:
        raise _NOT_FOUND
    return account


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> AccountOut:
    account = Account(
        name=body.name,
        category=body.category,
        status=body.status,
        address=body.address,
        notes=body.notes,
        assigned_rep_id=body.assigned_rep_id,
        location=await _resolve_point(body.lat, body.lng, body.address),
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return AccountOut.from_model(account)


@router.get("", response_model=Page[AccountOut])
async def list_accounts(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    category: AccountCategory | None = None,
    status_: AccountStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, description="Search by account name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Page[AccountOut]:
    filters = []
    # Reps only ever see their own accounts; managers see everything.
    if not is_manager(user):
        filters.append(Account.assigned_rep_id == user.id)
    if category:
        filters.append(Account.category == category)
    if status_:
        filters.append(Account.status == status_)
    if q:
        filters.append(Account.name.ilike(f"%{q}%"))

    total = await db.scalar(select(func.count()).select_from(Account).where(*filters))
    rows = (
        await db.scalars(
            select(Account)
            .where(*filters)
            .order_by(Account.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return Page(
        items=[AccountOut.from_model(a) for a in rows],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> AccountOut:
    return AccountOut.from_model(await _get_scoped(account_id, db, user))


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: uuid.UUID,
    body: AccountUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> AccountOut:
    account = await db.get(Account, account_id)
    if account is None:
        raise _NOT_FOUND

    data = body.model_dump(exclude_unset=True)
    for field in ("name", "category", "status", "address", "notes", "assigned_rep_id"):
        if field in data:
            setattr(account, field, data[field])

    # Recompute location: explicit coords win; else re-geocode a changed address.
    if body.lat is not None and body.lng is not None:
        account.location = to_point(body.lng, body.lat)
    elif "lat" in data and data["lat"] is None and "lng" in data and data["lng"] is None:
        account.location = None
    elif "address" in data and data["address"]:
        coords = await geocode(data["address"])
        if coords:
            account.location = to_point(coords[0], coords[1])

    await db.commit()
    await db.refresh(account)
    return AccountOut.from_model(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> None:
    account = await db.get(Account, account_id)
    if account is None:
        raise _NOT_FOUND
    await db.delete(account)
    await db.commit()
