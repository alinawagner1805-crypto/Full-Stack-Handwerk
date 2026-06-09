"""
test_stats.py – Smoke Tests für den /stats-Endpoint.

Verwendung:
    source .venv/bin/activate
    pip install pytest httpx
    pytest test_stats.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import Base, Prediction
from datetime import datetime

client = TestClient(app)

HEADERS = {"x-api-key": "dev-secret"}


@pytest.fixture(autouse=True)
def setup_db():
    """Erstellt Schema und fügt Testdaten ein, räumt danach auf."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add_all([
        Prediction(prediction="1", confidence=0.92, model_version="v1",
                   created_at=datetime(2026, 5, 1)),
        Prediction(prediction="7", confidence=0.85, model_version="v1",
                   created_at=datetime(2026, 5, 2)),
        Prediction(prediction="3", confidence=0.78, model_version="v2",
                   created_at=datetime(2026, 5, 3)),
    ])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


class TestStatsEndpoint:
    def test_stats_returns_200(self):
        r = client.get("/stats")
        assert r.status_code == 200

    def test_stats_total_predictions(self):
        r = client.get("/stats")
        assert r.json()["total_predictions"] == 3

    def test_stats_by_digit_keys(self):
        r = client.get("/stats")
        by_digit = r.json()["by_digit"]
        assert "1" in by_digit
        assert "7" in by_digit

    def test_stats_filter_model_version(self):
        r = client.get("/stats?model_version=v2")
        assert r.json()["total_predictions"] == 1

    def test_stats_filter_since(self):
        r = client.get("/stats?since=2026-05-02")
        assert r.json()["total_predictions"] == 2

    def test_stats_avg_confidence_range(self):
        r = client.get("/stats")
        avg = r.json()["avg_confidence"]
        assert 0.0 <= avg <= 1.0

    def test_stats_empty_db_returns_zero(self):
        # Tabelle leeren
        db = SessionLocal()
        db.query(Prediction).delete()
        db.commit()
        db.close()
        r = client.get("/stats")
        data = r.json()
        assert data["total_predictions"] == 0
        assert data["avg_confidence"] == 0.0

    def test_health_endpoint(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
