"""Contact endpoints, scoped to an account (Epic 1, Story 1.3)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, is_manager, require_manager
from app.models import Account, Contact, User
from app.schemas.contact import ContactCreate, ContactOut, ContactUpdate

router = APIRouter(tags=["contacts"])

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


async def _unset_other_primaries(
    db: AsyncSession, account_id: uuid.UUID, exclude: uuid.UUID | None
) -> None:
    """Keep at most one primary contact per account."""
    stmt = update(Contact).where(Contact.account_id == account_id, Contact.is_primary.is_(True))
    if exclude is not None:
        stmt = stmt.where(Contact.id != exclude)
    await db.execute(stmt.values(is_primary=False))


@router.get("/accounts/{account_id}/contacts", response_model=list[ContactOut])
async def list_contacts(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[ContactOut]:
    account = await db.get(Account, account_id)
    if account is None or (not is_manager(user) and account.assigned_rep_id != user.id):
        raise HTTPException(status_code=404, detail="Account not found")
    rows = (
        await db.scalars(
            select(Contact)
            .where(Contact.account_id == account_id)
            .order_by(Contact.is_primary.desc(), Contact.name)
        )
    ).all()
    return [ContactOut.model_validate(c) for c in rows]


@router.post(
    "/accounts/{account_id}/contacts",
    response_model=ContactOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    account_id: uuid.UUID,
    body: ContactCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> ContactOut:
    if await db.get(Account, account_id) is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if body.is_primary:
        await _unset_other_primaries(db, account_id, exclude=None)
    contact = Contact(account_id=account_id, **body.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return ContactOut.model_validate(contact)


@router.patch("/contacts/{contact_id}", response_model=ContactOut)
async def update_contact(
    contact_id: uuid.UUID,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> ContactOut:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise _NOT_FOUND
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(contact, field, value)
    if data.get("is_primary"):
        await _unset_other_primaries(db, contact.account_id, exclude=contact.id)
    await db.commit()
    await db.refresh(contact)
    return ContactOut.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> None:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise _NOT_FOUND
    await db.delete(contact)
    await db.commit()
