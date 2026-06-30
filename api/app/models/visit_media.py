"""Photo/media attached to a visit (Epic 3, Story 3.3)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import UUIDPkMixin


class VisitMedia(UUIDPkMixin, Base):
    __tablename__ = "visit_media"

    visit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Object key in the S3 bucket (not a public URL — views are presigned).
    key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
