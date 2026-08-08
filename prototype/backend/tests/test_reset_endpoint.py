"""API-level tests for POST /studies/reset ("Reset Demo", Milestone 9).

Uses isolated repository/engine/feedback instances via dependency_overrides
(same pattern as test_simulate_endpoint.py / test_feedback_api.py) so these
tests - which mutate worklist and feedback state - can't affect other test
files sharing the app's real singletons.
"""

import random

import pytest
from fastapi.testclient import TestClient

import app.services.study_workflow as workflow
from app.main import app
from app.repositories.feedback_repository import FeedbackRepository, get_feedback_repository
from app.repositories.study_repository import StudyRepository, get_study_repository
from app.services.ai_engine.simulated_engine import SimulatedAIEngine, get_ai_engine


@pytest.fixture()
def fast_client(monkeypatch):
    monkeypatch.setattr(workflow, "STUDY_ACQUIRING_SECONDS", 0.01)
    monkeypatch.setattr(workflow, "STUDY_AI_PROCESSING_SECONDS", 0.01)

    isolated_repo = StudyRepository()
    isolated_feedback_repo = FeedbackRepository()
    isolated_engine = SimulatedAIEngine(rng=random.Random(0))
    app.dependency_overrides[get_study_repository] = lambda: isolated_repo
    app.dependency_overrides[get_feedback_repository] = lambda: isolated_feedback_repo
    app.dependency_overrides[get_ai_engine] = lambda: isolated_engine
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_reset_on_pristine_state_returns_the_initial_three_studies(
    fast_client: TestClient,
) -> None:
    response = fast_client.post("/api/studies/reset")
    assert response.status_code == 200
    body = response.json()
    assert {s["id"] for s in body} == {"STU-001", "STU-004", "STU-005"}


def test_reset_removes_simulated_studies(fast_client: TestClient) -> None:
    fast_client.post("/api/studies/simulate")  # reveals STU-002
    assert len(fast_client.get("/api/studies").json()) == 4

    response = fast_client.post("/api/studies/reset")

    body = response.json()
    assert len(body) == 3
    assert not any(s["id"] == "STU-002" for s in body)
    # Reset also re-queues the reserve studies for another reveal pass.
    revealed_again = fast_client.post("/api/studies/simulate").json()
    assert revealed_again["id"] == "STU-002"


def test_reset_clears_reported_status_and_feedback(fast_client: TestClient) -> None:
    fast_client.post("/api/studies/STU-001/feedback", json={"decision": "Confirm"})
    reported = fast_client.get("/api/studies/STU-001").json()
    assert reported["study_status"] == "Reported"

    fast_client.post("/api/studies/reset")

    restored = fast_client.get("/api/studies/STU-001").json()
    assert restored["study_status"] == "Completed"
    # Feedback was cleared too - confirming again must succeed, not 409.
    second_confirm = fast_client.post(
        "/api/studies/STU-001/feedback", json={"decision": "Confirm"}
    )
    assert second_confirm.status_code == 201


def test_reset_restores_original_predictions_and_priorities(fast_client: TestClient) -> None:
    fast_client.post("/api/studies/reset")
    body = fast_client.get("/api/studies").json()
    by_id = {s["id"]: s for s in body}

    assert by_id["STU-001"]["priority"] == "Critical"
    assert by_id["STU-001"]["prediction"]["confidence"] == 0.93
    assert by_id["STU-004"]["priority"] == "Moderate"
    assert by_id["STU-005"]["priority"] == "Routine"
