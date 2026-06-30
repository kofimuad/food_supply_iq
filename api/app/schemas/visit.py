"""Visit schemas (Epic 3)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VisitOutcome
from app.models.visit import Visit
from app.utils.geo import point_to_latlng


class VisitCreate(BaseModel):
    notes: str | None = None
    outcome: VisitOutcome | None = None
    # Check-in GPS captured on the device (optional).
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    # Defaults to server time if the client doesn't supply it.
    occurred_at: datetime | None = None


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    rep_id: uuid.UUID | None
    occurred_at: datetime
    outcome: VisitOutcome | None
    notes: str | None
    lat: float | None = None
    lng: float | None = None

    @classmethod
    def from_model(cls, v: Visit) -> "VisitOut":
        latlng = point_to_latlng(v.location)
        return cls(
            id=v.id,
            account_id=v.account_id,
            rep_id=v.rep_id,
            occurred_at=v.occurred_at,
            outcome=v.outcome,
            notes=v.notes,
            lat=latlng[0] if latlng else None,
            lng=latlng[1] if latlng else None,
        )
