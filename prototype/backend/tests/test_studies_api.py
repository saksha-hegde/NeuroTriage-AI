"""API-level tests for the worklist endpoints (WL-01, WL-05)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_studies_returns_all_seed_studies() -> None:
    response = client.get("/api/studies")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 6


def test_list_studies_is_ordered_most_urgent_first() -> None:
    response = client.get("/api/studies")
    priorities = [s["priority"] for s in response.json()]
    rank = {"Critical": 0, "High": 1, "Moderate": 2, "Routine": 3}
    ranks = [rank[p] for p in priorities]
    assert ranks == sorted(ranks)


def test_get_study_returns_matching_study() -> None:
    response = client.get("/api/studies/STU-001")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "STU-001"
    assert body["patient_name"] == "Jordan Ellis"
    assert body["prediction"]["assessment"] == "Suspected ICH"


def test_get_study_404s_for_unknown_id() -> None:
    response = client.get("/api/studies/does-not-exist")
    assert response.status_code == 404
