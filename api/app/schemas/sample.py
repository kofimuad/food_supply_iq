"""Sample event schemas (Epic 4, Story 4.1)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SampleItemIn(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class SampleCreate(BaseModel):
    items: list[SampleItemIn] = Field(min_length=1)
    occurred_at: datetime | None = None
    visit_id: uuid.UUID | None = None


class SampleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    product_name: str
    quantity: int


class SampleOut(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    rep_id: uuid.UUID | None
    visit_id: uuid.UUID | None
    occurred_at: datetime
    items: list[SampleItemOut]
