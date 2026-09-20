"""Smoke tests: python -m pytest (run from the backend folder)."""
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.seed import seed

client = TestClient(app)


def setup_module() -> None:
    Base.metadata.create_all(engine)
    seed(reset=True)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_projects_seeded():
    assert len(client.get("/api/projects").json()) == 3


def test_every_dashboard_responds():
    for path in ["site-risk", "safety", "compliance", "insurance", "executive"]:
        assert client.get(f"/api/dashboards/{path}/1").status_code == 200


def test_agent_network_produces_a_score_and_report():
    body = client.post("/api/agents/run-network/1").json()
    assert 0 <= body["engine"]["project_risk_score"] <= 100
    assert body["report"]["body"].startswith("# ")


def test_logging_a_hazard_raises_its_severity():
    response = client.post(
        "/api/risks",
        json={"project_id": 1, "risk_type": "fall hazard", "zone": "Level 9", "description": "Open edge", "probability": 5, "impact": 5},
    )
    assert response.json()["severity"] == "critical"
