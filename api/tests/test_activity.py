"""Integration tests for the activity feed (Story 3.2)."""

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
        email=f"act-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


async def test_activity_feed_lists_visits_newest_first(client, manager):
    _, headers = manager
    rep = await _make_user(UserRole.rep)
    acc_id = (
        await client.post(
            "/accounts",
            json={
                "name": f"{PREFIX} A",
                "category": "grocery_store",
                "assigned_rep_id": str(rep.id),
            },
            headers=headers,
        )
    ).json()["id"]
    rep_headers = await _headers(client, rep.email)
    await client.post(
        f"/accounts/{acc_id}/visits", json={"outcome": "interested"}, headers=rep_headers
    )
    await client.post(
        f"/accounts/{acc_id}/visits", json={"outcome": "sample_given"}, headers=rep_headers
    )

    feed = await client.get("/activity", headers=headers)
    assert feed.status_code == 200, feed.text
    items = feed.json()["items"]
    ours = [e for e in items if e["account_name"] == f"{PREFIX} A"]
    assert len(ours) == 2
    assert all(e["type"] == "visit" for e in ours)
    # newest first
    assert ours[0]["occurred_at"] >= ours[1]["occurred_at"]

    # rep filter
    filtered = await client.get("/activity", params={"rep_id": str(rep.id)}, headers=headers)
    assert all(e["rep_id"] == str(rep.id) for e in filtered.json()["items"])

    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()


async def test_activity_feed_manager_only(client, manager):
    rep = await _make_user(UserRole.rep)
    rep_headers = await _headers(client, rep.email)
    assert (await client.get("/activity", headers=rep_headers)).status_code == 403
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()
