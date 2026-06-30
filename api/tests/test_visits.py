"""Integration tests for field visits (Story 3.1)."""

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
        email=f"vis-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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
async def _cleanup():
    yield
    async with SessionLocal() as db:
        await db.execute(delete(Account).where(Account.name.like(f"{PREFIX}%")))
        await db.commit()


async def _make_account(client, headers, **over) -> str:
    body = {"name": f"{PREFIX} Acct", "category": "grocery_store"}
    body.update(over)
    return (await client.post("/accounts", json=body, headers=headers)).json()["id"]


async def test_log_visit_attributes_rep_and_shows_in_profile(client, manager, rep):
    _, m_headers = manager
    rep_user, rep_headers = rep
    acc_id = await _make_account(client, m_headers, assigned_rep_id=str(rep_user.id))

    r = await client.post(
        f"/accounts/{acc_id}/visits",
        json={"notes": "dropped samples", "outcome": "sample_given", "lat": 38.92, "lng": -77.04},
        headers=rep_headers,
    )
    assert r.status_code == 201, r.text
    visit = r.json()
    assert visit["rep_id"] == str(rep_user.id)
    assert visit["outcome"] == "sample_given"
    assert visit["lat"] == 38.92 and visit["lng"] == -77.04

    # appears in account profile history + bumps the visit count
    profile = (await client.get(f"/accounts/{acc_id}/profile", headers=rep_headers)).json()
    assert profile["summary"]["visits"] == 1
    assert profile["recent_visits"][0]["id"] == visit["id"]


async def test_visit_requires_account_access(client, manager, rep):
    _, m_headers = manager
    _, rep_headers = rep
    # account unassigned → rep can't log a visit on it
    acc_id = await _make_account(client, m_headers)
    r = await client.post(
        f"/accounts/{acc_id}/visits", json={"outcome": "interested"}, headers=rep_headers
    )
    assert r.status_code == 404


async def test_list_and_get_visit(client, manager):
    _, headers = manager
    acc_id = await _make_account(client, headers)
    vid = (
        await client.post(
            f"/accounts/{acc_id}/visits", json={"notes": "intro call"}, headers=headers
        )
    ).json()["id"]

    listed = (await client.get(f"/accounts/{acc_id}/visits", headers=headers)).json()
    assert len(listed) == 1 and listed[0]["id"] == vid

    detail = await client.get(f"/visits/{vid}", headers=headers)
    assert detail.status_code == 200 and detail.json()["notes"] == "intro call"
