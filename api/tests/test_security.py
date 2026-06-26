"""Unit tests for password hashing + JWT (no DB)."""

import uuid

import jwt
import pytest
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("password123")
    assert hashed != "password123"
    assert verify_password("password123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_carries_role_and_type():
    uid = uuid.uuid4()
    token = create_access_token(uid, "manager")
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["role"] == "manager"
    assert payload["type"] == "access"


def test_refresh_token_type():
    token = create_refresh_token(uuid.uuid4(), "rep")
    assert decode_token(token)["type"] == "refresh"


def test_tampered_token_rejected():
    token = create_access_token(uuid.uuid4(), "rep")
    with pytest.raises(jwt.PyJWTError):
        decode_token(token + "tampered")
