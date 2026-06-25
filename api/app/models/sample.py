"""Sample event + line items (Epic 4) — the start of the core loop."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Sample(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "samples"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Optional link to the visit during which the sample was given.
    visit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("visits.id", ondelete="SET NULL"), nullable=True, index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    items: Mapped[list["SampleItem"]] = relationship(
        back_populates="sample", cascade="all, delete-orphan"
    )


class SampleItem(UUIDPkMixin, Base):
    __tablename__ = "sample_items"

    sample_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    sample: Mapped["Sample"] = relationship(back_populates="items")
