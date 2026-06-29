"""Contact schemas (Epic 1, Stories 1.2–1.3)."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    role: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=64)
    is_primary: bool = False


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=64)
    is_primary: bool | None = None


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    role: str | None
    phone: str | None
    is_primary: bool
