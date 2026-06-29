"""Audit trail of account pipeline status changes (Story 1.4)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import UUIDPkMixin
from app.models.enums import AccountStatus


class AccountStatusHistory(UUIDPkMixin, Base):
    __tablename__ = "account_status_history"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # The account_status enum type is created with the accounts table, so reuse it
    # here without re-emitting CREATE TYPE.
    from_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status", create_type=False), nullable=False
    )
    to_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status", create_type=False), nullable=False
    )
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
