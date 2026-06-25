"""Smoke test for the liveness endpoint (no DB required)."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
