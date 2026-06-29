"""Account status-change schemas (Story 1.4)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AccountStatus


class StatusChangeRequest(BaseModel):
    status: AccountStatus
    note: str | None = None


class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_status: AccountStatus
    to_status: AccountStatus
    changed_by_id: uuid.UUID | None
    changed_at: datetime
    note: str | None
