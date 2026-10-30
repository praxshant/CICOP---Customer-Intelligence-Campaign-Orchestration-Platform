"""Smoke tests for API startup behavior that does not require Redis."""

from fastapi.testclient import TestClient

from backend.api.main import app


def test_login_returns_unauthorized_when_redis_is_unavailable():
    """The optional rate limiter must not turn an invalid login into a 500."""
    with TestClient(app, headers={"host": "localhost"}, raise_server_exceptions=False) as client:
        response = client.post("/auth/login", json={"username": "missing", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
