"""Integration tests for orders (Stories 4.2–4.3)."""

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
        email=f"ord-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


async def _product(client, headers, name, price) -> str:
    body = {"name": f"{PREFIX} {name}", "price": price}
    return (await client.post("/products", json=body, headers=headers)).json()["id"]


async def test_trial_order_computes_value_and_links_sample(client, manager):
    _, headers = manager
    acc_id = await _account(client, headers)
    p1 = await _product(client, headers, "Jollof", 4.5)
    p2 = await _product(client, headers, "Oil", 9.0)

    sample_id = (
        await client.post(
            f"/accounts/{acc_id}/samples",
            json={"items": [{"product_id": p1, "quantity": 1}]},
            headers=headers,
        )
    ).json()["id"]

    r = await client.post(
        f"/accounts/{acc_id}/orders",
        json={
            "order_type": "trial",
            "sample_id": sample_id,
            "items": [{"product_id": p1, "quantity": 12}, {"product_id": p2, "quantity": 4}],
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    order = r.json()
    # 12*4.5 + 4*9.0 = 54 + 36 = 90
    assert order["total_value"] == 90.0
    assert order["order_type"] == "trial"
    assert order["sample_id"] == sample_id
    units = {i["product_id"]: i["unit_price"] for i in order["items"]}
    assert units[p1] == 4.5 and units[p2] == 9.0

    profile = (await client.get(f"/accounts/{acc_id}/profile", headers=headers)).json()
    assert profile["summary"]["orders"] == 1


async def test_repeat_order_type(client, manager):
    _, headers = manager
    acc_id = await _account(client, headers)
    p1 = await _product(client, headers, "Garri", 12.0)
    r = await client.post(
        f"/accounts/{acc_id}/orders",
        json={"order_type": "repeat", "items": [{"product_id": p1, "quantity": 2}]},
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["order_type"] == "repeat" and r.json()["total_value"] == 24.0
