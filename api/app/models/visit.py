"""Field visit model (Epic 3) — check-in with geo + outcome."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin
from app.models.enums import VisitOutcome


class Visit(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "visits"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Check-in GPS captured on the device.
    location: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    outcome: Mapped[VisitOutcome | None] = mapped_column(
        Enum(VisitOutcome, name="visit_outcome"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
