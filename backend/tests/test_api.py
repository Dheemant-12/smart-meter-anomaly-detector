from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_meters():
    response = client.get("/meters")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 10
    assert len(data["meters"]) == 10


def test_get_anomalies():
    response = client.get("/anomalies")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "anomalies" in data


def test_get_existing_meter():
    response = client.get("/meters/MTR_0002")

    assert response.status_code == 200

    data = response.json()

    assert data["meter_id"] == "MTR_0002"
    assert data["anomaly_count"] == 300


def test_get_missing_meter():
    response = client.get("/meters/MTR_9999")

    assert response.status_code == 404