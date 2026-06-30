"""User listing — supports the manager's rep filters (Story 3.2)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_manager
from app.models import User
from app.models.enums import UserRole
from app.schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
    role: UserRole | None = Query(default=None),
) -> list[UserOut]:
    stmt = select(User).order_by(User.full_name)
    if role is not None:
        stmt = stmt.where(User.role == role)
    rows = (await db.scalars(stmt)).all()
    return [UserOut.model_validate(u) for u in rows]
