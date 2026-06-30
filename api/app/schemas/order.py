"""Order schemas (Epic 4, Stories 4.2–4.3)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import OrderType


class OrderItemIn(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class OrderCreate(BaseModel):
    order_type: OrderType
    items: list[OrderItemIn] = Field(min_length=1)
    occurred_at: datetime | None = None
    # A trial order can trace back to the sample it converted from.
    sample_id: uuid.UUID | None = None
    visit_id: uuid.UUID | None = None


class OrderItemOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: float


class OrderOut(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    rep_id: uuid.UUID | None
    order_type: OrderType
    sample_id: uuid.UUID | None
    visit_id: uuid.UUID | None
    occurred_at: datetime
    total_value: float
    currency: str
    items: list[OrderItemOut]
