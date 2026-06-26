"""Auth dependencies: current user, role guards, rep scoping (Story 0.3)."""

import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.models.enums import UserRole
from app.security import decode_token

_bearer = HTTPBearer(auto_error=True)

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_token(creds.credentials)
    except jwt.PyJWTError as exc:
        raise _CREDENTIALS_ERROR from exc

    if payload.get("type") != "access":
        raise _CREDENTIALS_ERROR

    user_id = payload.get("sub")
    if not user_id:
        raise _CREDENTIALS_ERROR

    user = await db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR
    return user


async def require_manager(user: User = Depends(get_current_user)) -> User:
    """Guard for manager-only endpoints (sees all data)."""
    if user.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Manager role required"
        )
    return user


def is_manager(user: User) -> bool:
    return user.role == UserRole.manager
