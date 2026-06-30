"""Sample → Trial → Repeat funnel schemas (Epic 4, Story 4.4)."""

from pydantic import BaseModel


class FunnelStage(BaseModel):
    key: str  # sampled | trial | repeat
    label: str
    count: int
    # Conversion from the previous stage, as a percent (null for the first stage).
    conversion_from_prev: float | None
