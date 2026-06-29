"""Visit schemas (read models for Epic 1 profile; full CRUD lands in Epic 3)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import VisitOutcome


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    rep_id: uuid.UUID | None
    occurred_at: datetime
    outcome: VisitOutcome | None
    notes: str | None
