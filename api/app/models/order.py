"""Order event + line items (Epic 4) — trial and repeat orders."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin
from app.models.enums import OrderType


class Order(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, name="order_type"), nullable=False, index=True
    )
    # A trial order can trace back to the sample(s) it converted from (Story 4.2).
    sample_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("samples.id", ondelete="SET NULL"), nullable=True, index=True
    )
    visit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("visits.id", ondelete="SET NULL"), nullable=True, index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    # Denormalised total computed from items (Story 4.2).
    total_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(UUIDPkMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Price captured at order time so catalog price changes don't rewrite history.
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
