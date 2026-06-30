"""Account + Contact models — the whole market in one place (Epic 1)."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin
from app.models.enums import AccountCategory, AccountStatus


class Account(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[AccountCategory] = mapped_column(
        Enum(AccountCategory, name="account_category"), nullable=False
    )
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.lead,
        nullable=False,
        index=True,
    )
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # geography(Point, 4326); geoalchemy2 auto-creates a GiST spatial index.
    location: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Derived repeat-order metrics (Story 4.3): recomputed on order create and by
    # a nightly arq job. "Repeating" = the account has placed >= 2 orders.
    is_repeating: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    repeat_order_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_order_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Field rep this account is assigned to (rep scoping, Story 0.3 / 1.x).
    assigned_rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Contact(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "contacts"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="contacts")
