"""Integration tests for sample events (Story 4.1)."""

import uuid

import pytest_asyncio
from app.db import SessionLocal
from app.main import app
from app.models import Account, Product, User
from app.models.enums import UserRole
from app.security import hash_password
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

PASSWORD = "test-pass-123"
PREFIX = "ZZTEST"


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"smp-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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
        await db.execute(delete(Product).where(Product.name.like(f"{PREFIX}%")))
        await db.commit()


async def _account(client, headers) -> str:
    body = {"name": f"{PREFIX} A", "category": "grocery_store"}
    return (await client.post("/accounts", json=body, headers=headers)).json()["id"]


async def _product(client, headers, name="P") -> str:
    body = {"name": f"{PREFIX} {name}", "price": 5.0}
    return (await client.post("/products", json=body, headers=headers)).json()["id"]


async def test_record_sample_with_items(client, manager):
    _, headers = manager
    acc_id = await _account(client, headers)
    p1 = await _product(client, headers, "Jollof")
    p2 = await _product(client, headers, "Palm Oil")

    r = await client.post(
        f"/accounts/{acc_id}/samples",
        json={"items": [{"product_id": p1, "quantity": 2}, {"product_id": p2, "quantity": 1}]},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    sample = r.json()
    assert len(sample["items"]) == 2
    qty = {i["product_id"]: i["quantity"] for i in sample["items"]}
    assert qty[p1] == 2 and qty[p2] == 1
    assert all(i["product_name"].startswith(PREFIX) for i in sample["items"])

    # shows on the account profile summary + list
    profile = (await client.get(f"/accounts/{acc_id}/profile", headers=headers)).json()
    assert profile["summary"]["samples"] == 1
    listed = (await client.get(f"/accounts/{acc_id}/samples", headers=headers)).json()
    assert len(listed) == 1


async def test_sample_rejects_unknown_product(client, manager):
    _, headers = manager
    acc_id = await _account(client, headers)
    r = await client.post(
        f"/accounts/{acc_id}/samples",
        json={"items": [{"product_id": str(uuid.uuid4()), "quantity": 1}]},
        headers=headers,
    )
    assert r.status_code == 400


async def test_sample_requires_items(client, manager):
    _, headers = manager
    acc_id = await _account(client, headers)
    r = await client.post(f"/accounts/{acc_id}/samples", json={"items": []}, headers=headers)
    assert r.status_code == 422
