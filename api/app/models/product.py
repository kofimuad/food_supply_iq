"""Product catalog (Epic 2)."""

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Product(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    pack_size: Mapped[str | None] = mapped_column(String(64), nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    # Soft-delete via active flag so historical samples/orders keep their product.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
