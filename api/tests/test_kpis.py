"""Integration tests for the KPI dashboard (Story 6.1)."""

import uuid

import pytest_asyncio
from app.db import SessionLocal
from app.main import app
from app.models import Account, KpiTarget, Product, User
from app.models.enums import UserRole
from app.security import hash_password
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

PASSWORD = "test-pass-123"
PREFIX = "ZZTEST"


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"kpi-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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
        await db.execute(delete(KpiTarget))
        await db.commit()


async def test_kpis_shape_and_revenue(client, manager):
    _, headers = manager
    acc = (
        await client.post(
            "/accounts", json={"name": f"{PREFIX} A", "category": "grocery_store"}, headers=headers
        )
    ).json()["id"]
    p = (
        await client.post("/products", json={"name": f"{PREFIX} P", "price": 10.0}, headers=headers)
    ).json()["id"]

    # KPIs are DB-wide (manager view), so measure the delta this order produces.
    def by_key(resp):
        return {m["key"]: m for m in resp.json()["metrics"]}

    before = by_key(await client.get("/kpis", headers=headers))
    assert {"new_accounts", "visits", "samples", "trial_orders", "repeat_orders", "revenue"} <= (
        before.keys()
    )
    # spark series present and aligned to the window
    assert len(before["revenue"]["spark"]) == len(before["visits"]["spark"]) > 0

    await client.post(
        f"/accounts/{acc}/orders",
        json={"order_type": "trial", "items": [{"product_id": p, "quantity": 3}]},
        headers=headers,
    )

    after = by_key(await client.get("/kpis", headers=headers))
    assert after["revenue"]["value"] - before["revenue"]["value"] == 30.0
    assert after["trial_orders"]["value"] - before["trial_orders"]["value"] == 1


async def test_targets_roundtrip_and_attach(client, manager):
    _, headers = manager
    put = await client.put(
        "/kpis/targets", json={"targets": {"visits": 50, "revenue": 1000}}, headers=headers
    )
    assert put.status_code == 200
    assert put.json()["targets"]["visits"] == 50

    kpis = (await client.get("/kpis", headers=headers)).json()["metrics"]
    by_key = {m["key"]: m for m in kpis}
    assert by_key["visits"]["target"] == 50
    assert by_key["revenue"]["target"] == 1000
    assert by_key["samples"]["target"] is None


async def test_kpis_manager_only(client):
    rep = await _make_user(UserRole.rep)
    rep_headers = await _headers(client, rep.email)
    assert (await client.get("/kpis", headers=rep_headers)).status_code == 403
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == rep.id))
        await db.commit()
