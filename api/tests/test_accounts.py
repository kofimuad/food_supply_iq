"""Integration tests for account CRUD (requires the dev Postgres to be up)."""

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
PREFIX = "ZZTEST"  # all test accounts use this name prefix for easy cleanup


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"acct-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


@pytest_asyncio.fixture
async def rep(client):
    user = await _make_user(UserRole.rep)
    headers = await _headers(client, user.email)
    yield user, headers
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == user.id))
        await db.commit()


@pytest_asyncio.fixture(autouse=True)
async def _cleanup_accounts():
    yield
    async with SessionLocal() as db:
        await db.execute(delete(Account).where(Account.name.like(f"{PREFIX}%")))
        await db.commit()


def _payload(**over):
    body = {"name": f"{PREFIX} Market", "category": "grocery_store"}
    body.update(over)
    return body


async def test_create_requires_manager(client, rep):
    _, rep_headers = rep
    assert (await client.post("/accounts", json=_payload())).status_code in (401, 403)
    assert (await client.post("/accounts", json=_payload(), headers=rep_headers)).status_code == 403


async def test_create_with_coords_and_get(client, manager):
    _, headers = manager
    r = await client.post(
        "/accounts",
        json=_payload(lat=38.9213, lng=-77.0421, status="lead"),
        headers=headers,
    )
    assert r.status_code == 201, r.text
    acc = r.json()
    assert acc["lat"] == 38.9213 and acc["lng"] == -77.0421
    assert acc["category"] == "grocery_store"

    got = await client.get(f"/accounts/{acc['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["id"] == acc["id"]


async def test_create_without_coords_has_no_location(client, manager):
    # No Mapbox token in tests → geocoding is skipped, location stays null.
    _, headers = manager
    r = await client.post("/accounts", json=_payload(address="123 Nowhere St"), headers=headers)
    assert r.status_code == 201
    assert r.json()["lat"] is None and r.json()["lng"] is None


async def test_list_filters_by_category(client, manager):
    _, headers = manager
    for name, cat in [(f"{PREFIX} Groc", "grocery_store"), (f"{PREFIX} Whole", "wholesaler")]:
        await client.post("/accounts", json=_payload(name=name, category=cat), headers=headers)

    r = await client.get(
        "/accounts", params={"category": "wholesaler", "q": PREFIX}, headers=headers
    )
    assert r.status_code == 200
    body = r.json()
    assert all(a["category"] == "wholesaler" for a in body["items"])
    assert any(a["name"] == f"{PREFIX} Whole" for a in body["items"])


async def test_rep_scoping(client, manager, rep):
    _, m_headers = manager
    rep_user, rep_headers = rep
    other = await _make_user(UserRole.rep)
    other_headers = await _headers(client, other.email)

    r = await client.post(
        "/accounts", json=_payload(assigned_rep_id=str(rep_user.id)), headers=m_headers
    )
    acc_id = r.json()["id"]

    # The assigned rep sees it; another rep does not.
    mine = await client.get("/accounts", params={"q": PREFIX}, headers=rep_headers)
    assert any(a["id"] == acc_id for a in mine.json()["items"])
    theirs = await client.get("/accounts", params={"q": PREFIX}, headers=other_headers)
    assert all(a["id"] != acc_id for a in theirs.json()["items"])
    # And a direct fetch by the wrong rep 404s.
    assert (await client.get(f"/accounts/{acc_id}", headers=other_headers)).status_code == 404

    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == other.id))
        await db.commit()


async def test_update_and_delete(client, manager):
    _, headers = manager
    acc_id = (await client.post("/accounts", json=_payload(), headers=headers)).json()["id"]

    upd = await client.patch(
        f"/accounts/{acc_id}",
        json={"status": "sampled", "name": f"{PREFIX} Renamed"},
        headers=headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "sampled" and upd.json()["name"] == f"{PREFIX} Renamed"

    assert (await client.delete(f"/accounts/{acc_id}", headers=headers)).status_code == 204
    assert (await client.get(f"/accounts/{acc_id}", headers=headers)).status_code == 404
