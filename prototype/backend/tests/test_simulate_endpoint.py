"""API-level tests for POST /studies/simulate.

Uses isolated repository/engine instances via dependency_overrides (rather
than the app's shared singletons) so these tests don't pollute state for
other test modules that share the same `app` object.
"""

import random

import pytest
from fastapi.testclient import TestClient

import app.services.study_workflow as workflow
from app.main import app
from app.repositories.study_repository import StudyRepository, get_study_repository
from app.services.ai_engine.simulated_engine import SimulatedAIEngine, get_ai_engine


@pytest.fixture()
def fast_client(monkeypatch):
    monkeypatch.setattr(workflow, "STUDY_ACQUIRING_SECONDS", 0.01)
    monkeypatch.setattr(workflow, "STUDY_AI_PROCESSING_SECONDS", 0.01)

    # Create the instances once and close over them - dependency_overrides
    # calls this callable on every resolution, so returning a fresh instance
    # each time would give each request its own throwaway repository.
    isolated_repo = StudyRepository()
    isolated_engine = SimulatedAIEngine(rng=random.Random(0))
    app.dependency_overrides[get_study_repository] = lambda: isolated_repo
    app.dependency_overrides[get_ai_engine] = lambda: isolated_engine
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_simulate_creates_study_in_acquiring_status(fast_client: TestClient) -> None:
    response = fast_client.post("/api/studies/simulate")
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "STU-007"
    assert body["study_status"] == "Acquiring"
    assert body["ai_status"] is None
    assert body["priority"] is None


def test_simulate_progresses_to_ready_with_priority(fast_client: TestClient) -> None:
    """TestClient runs background tasks to completion before returning, so
    by the time we follow up with a GET, the (fast, monkeypatched) workflow
    has already finished."""
    created = fast_client.post("/api/studies/simulate").json()

    follow_up = fast_client.get(f"/api/studies/{created['id']}")
    body = follow_up.json()
    assert body["study_status"] == "Completed"
    assert body["ai_status"] == "Ready"
    assert body["priority"] is not None
    assert body["prediction"] is not None


def test_simulated_study_appears_in_worklist(fast_client: TestClient) -> None:
    fast_client.post("/api/studies/simulate")
    worklist = fast_client.get("/api/studies").json()

    assert len(worklist) == 7
    assert any(s["id"] == "STU-007" for s in worklist)
