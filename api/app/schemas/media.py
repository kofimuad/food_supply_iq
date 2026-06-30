"""Visit media schemas (Epic 3, Story 3.3)."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class PresignRequest(BaseModel):
    content_type: str = "image/jpeg"


class PresignResponse(BaseModel):
    key: str
    upload_url: str
    method: str = "PUT"


class AttachMediaRequest(BaseModel):
    key: str
    content_type: str | None = None


class MediaOut(BaseModel):
    id: uuid.UUID
    visit_id: uuid.UUID
    content_type: str | None
    created_at: datetime
    # Presigned GET URL for viewing/thumbnails (expires).
    view_url: str
