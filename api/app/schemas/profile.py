"""Aggregated account profile (Epic 1, Story 1.2)."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.account import AccountOut
from app.schemas.contact import ContactOut
from app.schemas.visit import VisitOut


class ProfileSummary(BaseModel):
    visits: int
    samples: int
    orders: int
    last_visit_at: datetime | None


class AccountProfile(BaseModel):
    account: AccountOut
    contacts: list[ContactOut]
    recent_visits: list[VisitOut]
    summary: ProfileSummary
