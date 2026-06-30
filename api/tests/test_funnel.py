"""Integration tests for the Sample→Trial→Repeat funnel (Story 4.4)."""

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
        email=f"fun-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


async def _account(client, headers, name) -> str:
    body = {"name": f"{PREFIX} {name}", "category": "grocery_store"}
    return (await client.post("/accounts", json=body, headers=headers)).json()["id"]


async def _product(client, headers) -> str:
    return (
        await client.post("/products", json={"name": f"{PREFIX} P", "price": 5.0}, headers=headers)
    ).json()["id"]


async def test_funnel_counts_and_conversion(client, manager):
    _, headers = manager
    p = await _product(client, headers)
    a1 = await _account(client, headers, "A1")
    a2 = await _account(client, headers, "A2")
    a3 = await _account(client, headers, "A3")

    async def sample(acc):
        await client.post(
            f"/accounts/{acc}/samples",
            json={"items": [{"product_id": p, "quantity": 1}]},
            headers=headers,
        )

    async def order(acc, kind):
        await client.post(
            f"/accounts/{acc}/orders",
            json={"order_type": kind, "items": [{"product_id": p, "quantity": 1}]},
            headers=headers,
        )

    # a1: sampled+trial+repeat, a2: sampled+trial, a3: sampled only
    for a in (a1, a2, a3):
        await sample(a)
    await order(a1, "trial")
    await order(a1, "repeat")
    await order(a2, "trial")

    stages = (await client.get("/funnel", headers=headers)).json()
    by_key = {s["key"]: s for s in stages}
    # only our ZZTEST accounts exist in this fresh-ish window, but other data may
    # exist; assert our accounts are counted at the right stages via drill-down.
    async def stage_ids(stage):
        resp = await client.get(f"/funnel/accounts?stage={stage}", headers=headers)
        return {a["id"] for a in resp.json()}

    sampled_ids = await stage_ids("sampled")
    trial_ids = await stage_ids("trial")
    repeat_ids = await stage_ids("repeat")
    assert {a1, a2, a3} <= sampled_ids
    assert a1 in trial_ids and a2 in trial_ids and a3 not in trial_ids
    assert a1 in repeat_ids and a2 not in repeat_ids

    # stage shape: 3 stages, conversions present for trial/repeat
    assert by_key["sampled"]["conversion_from_prev"] is None
    assert by_key["trial"]["conversion_from_prev"] is not None
