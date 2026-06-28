"""Helpers to convert between lat/lng and PostGIS geography(Point, 4326)."""

from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import to_shape


def to_point(lng: float, lat: float) -> WKTElement:
    """Build a geography Point literal. PostGIS order is (lng, lat)."""
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def point_to_latlng(element: WKBElement | None) -> tuple[float, float] | None:
    """Extract (lat, lng) from a stored geography Point, or None."""
    if element is None:
        return None
    point = to_shape(element)
    return (point.y, point.x)  # shapely: x=lng, y=lat
