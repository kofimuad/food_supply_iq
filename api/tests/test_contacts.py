"""Integration tests for account contacts (Story 1.3)."""

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
        email=f"ct-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


async def _make_account(client, headers) -> str:
    body = {"name": f"{PREFIX} Acct", "category": "grocery_store"}
    return (await client.post("/accounts", json=body, headers=headers)).json()["id"]


async def test_contact_crud_and_single_primary(client, manager):
    _, headers = manager
    acc_id = await _make_account(client, headers)

    # create two primary contacts; only the latest should remain primary
    c1 = (
        await client.post(
            f"/accounts/{acc_id}/contacts",
            json={"name": "Grace", "role": "Owner", "phone": "+1 202 555 0142", "is_primary": True},
            headers=headers,
        )
    ).json()
    c2 = (
        await client.post(
            f"/accounts/{acc_id}/contacts",
            json={"name": "Yaw", "is_primary": True},
            headers=headers,
        )
    ).json()
    assert c1["is_primary"] and c2["is_primary"]

    listed = (await client.get(f"/accounts/{acc_id}/contacts", headers=headers)).json()
    primaries = [c for c in listed if c["is_primary"]]
    assert len(listed) == 2
    assert len(primaries) == 1 and primaries[0]["id"] == c2["id"]

    # update + delete
    upd = await client.patch(f"/contacts/{c1['id']}", json={"role": "Manager"}, headers=headers)
    assert upd.status_code == 200 and upd.json()["role"] == "Manager"

    assert (await client.delete(f"/contacts/{c2['id']}", headers=headers)).status_code == 204
    remaining = (await client.get(f"/accounts/{acc_id}/contacts", headers=headers)).json()
    assert len(remaining) == 1 and remaining[0]["id"] == c1["id"]


async def test_contact_create_requires_manager(client, manager):
    _, headers = manager
    acc_id = await _make_account(client, headers)
    rep = await _make_user(UserRole.rep)
    rep_headers = await _headers(client, rep.email)

    r = await client.post(
        f"/accounts/{acc_id}/contacts", json={"name": "X"}, headers=rep_headers
    )
    assert r.status_code == 403

    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()
