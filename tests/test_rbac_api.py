from fastapi.testclient import TestClient

from app.main import app


def test_registry_requires_auth_headers() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/registry")
    assert response.status_code == 401
