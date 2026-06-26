"""Integration tests for the auth flow (requires the dev Postgres to be up)."""

import uuid

import pytest_asyncio
from app.db import SessionLocal
from app.main import app
from app.models import User
from app.models.enums import UserRole
from app.security import hash_password
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

PASSWORD = "test-pass-123"


@pytest_asyncio.fixture
async def manager_user():
    """Create a throwaway manager, yield it, then delete it."""
    user = User(
        email=f"auth-test-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
        full_name="Auth Test Manager",
        role=UserRole.manager,
        hashed_password=hash_password(PASSWORD),
    )
    async with SessionLocal() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    yield user
    async with SessionLocal() as db:
        await db.execute(delete(User).where(User.id == user.id))
        await db.commit()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_login_me_refresh(client, manager_user):
    # login
    r = await client.post(
        "/auth/login", json={"email": manager_user.email, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert tokens["token_type"] == "bearer"

    # me
    r = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert r.status_code == 200
    assert r.json()["email"] == manager_user.email
    assert r.json()["role"] == "manager"

    # refresh rotates the pair
    r = await client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_wrong_password_rejected(client, manager_user):
    r = await client.post(
        "/auth/login", json={"email": manager_user.email, "password": "nope"}
    )
    assert r.status_code == 401


async def test_me_requires_token(client):
    r = await client.get("/auth/me")
    assert r.status_code in (401, 403)


async def test_access_token_rejected_on_refresh(client, manager_user):
    r = await client.post(
        "/auth/login", json={"email": manager_user.email, "password": PASSWORD}
    )
    access = r.json()["access_token"]
    # using an access token where a refresh token is required must fail
    r = await client.post("/auth/refresh", json={"refresh_token": access})
    assert r.status_code == 401
