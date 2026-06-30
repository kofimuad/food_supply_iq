"""Integration tests for geo endpoints (Epic 5)."""

import uuid

import pytest_asyncio
from app.db import SessionLocal
from app.main import app
from app.models import Account, User
from app.models.enums import UserRole
from app.security import hash_password
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

PASSWORD = "test-pass-123"
PREFIX = "ZZTEST"


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"geo-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
        full_name=f"Test {role.value}",
        role=role,
        hashed_password=hash_password(PASSWORD),
    )
    async with SessionLocal() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def _headers(client: AsyncClient, email: str) -> dict[str, str]:
    r = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def manager(client):
    user = await _make_user(UserRole.manager)
    headers = await _headers(client, user.email)
    yield user, headers
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == user.id))
        await db.commit()


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    async with SessionLocal() as db:
        await db.execute(delete(Account).where(Account.name.like(f"{PREFIX}%")))
        await db.commit()


async def _acct(client, headers, name, lat, lng) -> str:
    body = {"name": f"{PREFIX} {name}", "category": "grocery_store", "lat": lat, "lng": lng}
    return (await client.post("/accounts", json=body, headers=headers)).json()["id"]


async def test_nearby_radius(client, manager):
    _, headers = manager
    # two DMV points close together, one in Accra far away
    near1 = await _acct(client, headers, "DMV1", 38.9213, -77.0421)
    near2 = await _acct(client, headers, "DMV2", 38.9959, -77.0260)
    await _acct(client, headers, "Accra", 5.5470, -0.2010)

    r = await client.get(
        "/geo/accounts/nearby",
        params={"lat": 38.95, "lng": -77.03, "radius_m": 20000},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    names = {a["name"] for a in r.json()}
    ids = {a["id"] for a in r.json()}
    assert near1 in ids and near2 in ids
    assert f"{PREFIX} Accra" not in names  # far point excluded by the radius


async def test_clusters_manager_only(client, manager):
    _, headers = manager
    await _acct(client, headers, "DMV1", 38.9213, -77.0421)
    await _acct(client, headers, "Accra", 5.5470, -0.2010)

    r = await client.get("/geo/accounts/clusters", params={"precision": 0}, headers=headers)
    assert r.status_code == 200
    # two far-apart points -> at least two distinct cells
    assert len(r.json()) >= 2
    assert all({"lat", "lng", "count"} <= c.keys() for c in r.json())

    rep = await _make_user(UserRole.rep)
    rep_headers = await _headers(client, rep.email)
    assert (await client.get("/geo/accounts/clusters", headers=rep_headers)).status_code == 403
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()
