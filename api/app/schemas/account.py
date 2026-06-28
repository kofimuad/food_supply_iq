"""Account schemas (Epic 1)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.account import Account
from app.models.enums import AccountCategory, AccountStatus
from app.utils.geo import point_to_latlng


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: AccountCategory
    status: AccountStatus = AccountStatus.lead
    address: str | None = None
    notes: str | None = None
    # Optional explicit coordinates; if omitted, the address is geocoded on save.
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    assigned_rep_id: uuid.UUID | None = None


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: AccountCategory | None = None
    status: AccountStatus | None = None
    address: str | None = None
    notes: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    assigned_rep_id: uuid.UUID | None = None


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: AccountCategory
    status: AccountStatus
    address: str | None
    lat: float | None
    lng: float | None
    notes: str | None
    last_verified_at: datetime | None
    assigned_rep_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, a: Account) -> "AccountOut":
        latlng = point_to_latlng(a.location)
        return cls(
            id=a.id,
            name=a.name,
            category=a.category,
            status=a.status,
            address=a.address,
            lat=latlng[0] if latlng else None,
            lng=latlng[1] if latlng else None,
            notes=a.notes,
            last_verified_at=a.last_verified_at,
            assigned_rep_id=a.assigned_rep_id,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
