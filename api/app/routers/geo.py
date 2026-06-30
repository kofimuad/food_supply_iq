"""Geospatial endpoints — rep map + manager territory (Epic 5)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, is_manager, require_manager
from app.models import Account, User
from app.schemas.account import AccountOut
from app.schemas.geo import ClusterCell
from app.utils.geo import to_point

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/accounts/nearby", response_model=list[AccountOut])
async def nearby_accounts(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_m: int = Query(default=5000, ge=1, le=200_000),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[AccountOut]:
    """Accounts within `radius_m` metres of a point (rep 'near me'). Rep-scoped."""
    filters = [
        Account.location.isnot(None),
        func.ST_DWithin(Account.location, to_point(lng, lat), radius_m),
    ]
    if not is_manager(user):
        filters.append(Account.assigned_rep_id == user.id)
    rows = (await db.scalars(select(Account).where(*filters))).all()
    return [AccountOut.from_model(a) for a in rows]


@router.get("/accounts/clusters", response_model=list[ClusterCell])
async def account_clusters(
    precision: int = Query(default=1, ge=0, le=4),
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> list[ClusterCell]:
    """Grid rollup of geocoded accounts into area cells (manager territory view).

    `precision` is decimal places to snap to: 1 ~= 11 km cells, 2 ~= 1.1 km.
    """
    sql = text(
        """
        SELECT avg(ST_Y(geom)) AS lat, avg(ST_X(geom)) AS lng, count(*) AS n
        FROM (
            SELECT location::geometry AS geom,
                   round(ST_Y(location::geometry)::numeric, :p) AS gy,
                   round(ST_X(location::geometry)::numeric, :p) AS gx
            FROM accounts
            WHERE location IS NOT NULL
        ) t
        GROUP BY gy, gx
        ORDER BY n DESC
        """
    )
    rows = (await db.execute(sql, {"p": precision})).all()
    return [ClusterCell(lat=float(r.lat), lng=float(r.lng), count=int(r.n)) for r in rows]
