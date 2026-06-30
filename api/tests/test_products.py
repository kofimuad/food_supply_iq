"""Integration tests for the product catalog (Story 2.1)."""

import uuid

import pytest_asyncio
from app.db import SessionLocal
from app.main import app
from app.models import Product, User
from app.models.enums import UserRole
from app.security import hash_password
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

PASSWORD = "test-pass-123"
PREFIX = "ZZTEST"


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"prod-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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
        await db.execute(delete(Product).where(Product.name.like(f"{PREFIX}%")))
        await db.commit()


def _payload(**over):
    body = {"name": f"{PREFIX} Garri", "pack_size": "5kg", "price": 12.5, "currency": "USD"}
    body.update(over)
    return body


async def test_create_requires_manager(client, manager):
    _, headers = manager
    rep = await _make_user(UserRole.rep)
    rep_headers = await _headers(client, rep.email)
    assert (await client.post("/products", json=_payload(), headers=rep_headers)).status_code == 403
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()


async def test_crud_and_soft_delete(client, manager):
    _, headers = manager
    created = await client.post("/products", json=_payload(), headers=headers)
    assert created.status_code == 201, created.text
    p = created.json()
    assert p["price"] == 12.5 and p["is_active"] is True

    # update price
    upd = await client.patch(f"/products/{p['id']}", json={"price": 13.0}, headers=headers)
    assert upd.status_code == 200 and upd.json()["price"] == 13.0

    # soft-delete deactivates rather than removing
    deld = await client.delete(f"/products/{p['id']}", headers=headers)
    assert deld.status_code == 200 and deld.json()["is_active"] is False

    # default list hides inactive; include_inactive shows it
    active = (await client.get("/products", params={"q": PREFIX}, headers=headers)).json()
    assert all(item["id"] != p["id"] for item in active["items"])
    withinactive = (
        await client.get(
            "/products", params={"q": PREFIX, "include_inactive": True}, headers=headers
        )
    ).json()
    assert any(item["id"] == p["id"] for item in withinactive["items"])

    # still fetchable by id, and can be reactivated
    react = await client.patch(f"/products/{p['id']}", json={"is_active": True}, headers=headers)
    assert react.status_code == 200 and react.json()["is_active"] is True
