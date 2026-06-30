"""Product catalog schemas (Epic 2)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    pack_size: str | None = Field(default=None, max_length=64)
    price: float | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    pack_size: str | None = Field(default=None, max_length=64)
    price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_active: bool | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    pack_size: str | None
    price: float | None
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
