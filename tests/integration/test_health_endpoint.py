from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_components() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert "sqlite" in body["components"]
    assert "chromadb" in body["components"]
    assert "session_store" in body["components"]
    assert "query_cache" in body["components"]
