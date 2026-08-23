"""Liveness check used by Render and the frontend AuthGate."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_healthy_payload():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "degraded"}
    assert data["service"] == "journal-app-backend"
    assert data["database"] in {"ok", "error", "unknown"}
