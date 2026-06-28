"""Shared schema helpers."""

from pydantic import BaseModel


class Page[T](BaseModel):
    """A paginated slice of results."""

    items: list[T]
    total: int
    limit: int
    offset: int
