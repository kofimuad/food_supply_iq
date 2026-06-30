"""Geo / territory schemas (Epic 5)."""

from pydantic import BaseModel


class ClusterCell(BaseModel):
    """An aggregated area of accounts (grid rollup) for the territory map."""

    lat: float
    lng: float
    count: int
