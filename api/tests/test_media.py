"""End-to-end test for visit media (Story 3.3) — exercises the real MinIO.

Requires the dev MinIO (docker compose up) to be reachable on localhost:9000.
"""

import uuid

import httpx
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
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c6360000002000154a24f5f0000000049454e44ae426082"
)


async def _make_user(role: UserRole) -> User:
    user = User(
        email=f"med-{role.value}-{uuid.uuid4().hex[:8]}@foodsupplyiq.com",
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


async def test_visit_photo_roundtrip(client, manager):
    _, headers = manager
    acc_id = (
        await client.post(
            "/accounts", json={"name": f"{PREFIX} A", "category": "grocery_store"}, headers=headers
        )
    ).json()["id"]
    visit_id = (
        await client.post(
            f"/accounts/{acc_id}/visits", json={"outcome": "interested"}, headers=headers
        )
    ).json()["id"]

    # 1. presign
    pre = await client.post(
        f"/visits/{visit_id}/media/presign", json={"content_type": "image/png"}, headers=headers
    )
    assert pre.status_code == 200, pre.text
    key, upload_url = pre.json()["key"], pre.json()["upload_url"]

    # 2. upload the bytes directly to MinIO via the presigned URL
    async with httpx.AsyncClient() as raw:
        put = await raw.put(upload_url, content=PNG, headers={"Content-Type": "image/png"})
        assert put.status_code in (200, 204), put.text

    # 3. attach to the visit
    att = await client.post(
        f"/visits/{visit_id}/media",
        json={"key": key, "content_type": "image/png"},
        headers=headers,
    )
    assert att.status_code == 201, att.text
    media_id = att.json()["id"]
    assert att.json()["view_url"].startswith("http")

    # 4. list + download via the presigned view URL
    listed = (await client.get(f"/visits/{visit_id}/media", headers=headers)).json()
    assert len(listed) == 1 and listed[0]["id"] == media_id
    async with httpx.AsyncClient() as raw:
        got = await raw.get(listed[0]["view_url"])
        assert got.status_code == 200 and got.content == PNG

    # 5. delete
    assert (await client.delete(f"/media/{media_id}", headers=headers)).status_code == 204
    assert (await client.get(f"/visits/{visit_id}/media", headers=headers)).json() == []
