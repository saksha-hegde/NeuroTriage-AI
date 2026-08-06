"""Smoke test: confirms the app boots and basic routing/CORS wiring works."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_studies_router_is_wired() -> None:
    response = client.get("/api/studies/ping")
    assert response.status_code == 200
