"""Activity feed schema (Epic 3, Story 3.2)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ActivityEvent(BaseModel):
    type: Literal["visit", "sample", "order"]
    id: uuid.UUID
    account_id: uuid.UUID
    account_name: str
    rep_id: uuid.UUID | None
    occurred_at: datetime
    detail: str


class ActivityFeed(BaseModel):
    items: list[ActivityEvent]
    # Pass back as `before` to page older events; null when no more.
    next_cursor: datetime | None
