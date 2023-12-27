from fastapi.testclient import TestClient


def test_monitoring_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
