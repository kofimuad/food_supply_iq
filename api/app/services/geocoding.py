"""Address geocoding via the Mapbox Geocoding API (Story 1.1).

Degrades gracefully: if no token is configured or the lookup fails, returns
None so account creation still succeeds (the account just has no location yet).
"""

import logging
from urllib.parse import quote

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_MAPBOX_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"


async def geocode(address: str) -> tuple[float, float] | None:
    """Geocode an address to (lng, lat), or None if unavailable."""
    settings = get_settings()
    if not settings.mapbox_token or not address.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                _MAPBOX_URL.format(query=quote(address)),
                params={"access_token": settings.mapbox_token, "limit": 1},
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            if not features:
                return None
            lng, lat = features[0]["center"]
            return (float(lng), float(lat))
    except (httpx.HTTPError, KeyError, ValueError, IndexError) as exc:
        logger.warning("Geocoding failed for %r: %s", address, exc)
        return None
