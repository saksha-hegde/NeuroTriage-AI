"""API-level tests for POST /studies/simulate.

Uses isolated repository/engine instances via dependency_overrides (rather
than the app's shared singletons) so these tests don't pollute state for
other test modules that share the same `app` object.

Milestone 9: the first three calls reveal the real held-back DICOM studies
(STU-002/003/006) with their own pre-calibrated predictions; only the fourth
call (and beyond) falls back to a fully fabricated study via the simulated
AI engine, exactly as this endpoint behaved before.
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


def test_first_simulate_reveals_the_first_real_reserve_study(fast_client: TestClient) -> None:
    response = fast_client.post("/api/studies/simulate")
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "STU-002"
    assert body["patient_name"] == "Wei Zhang"
    assert body["study_status"] == "Acquiring"
    assert body["ai_status"] is None
    assert body["priority"] is None


def test_revealed_study_reaches_ready_with_its_real_calibrated_prediction(
    fast_client: TestClient,
) -> None:
    """TestClient runs background tasks to completion before returning, so
    by the time we follow up with a GET, the (fast, monkeypatched) workflow
    has already finished."""
    created = fast_client.post("/api/studies/simulate").json()

    follow_up = fast_client.get(f"/api/studies/{created['id']}").json()
    assert follow_up["study_status"] == "Completed"
    assert follow_up["ai_status"] == "Ready"
    # The real calibrated values from seed_studies.json, not a random
    # AI-engine-generated prediction.
    assert follow_up["priority"] == "Critical"
    assert follow_up["prediction"]["assessment"] == "Suspected ICH"
    assert follow_up["prediction"]["confidence"] == 0.88
    assert follow_up["prediction"]["hemorrhage_location"] == "Left frontal lobe"
    assert follow_up["prediction"]["overlay_region"]["slice_index"] == 35


def test_second_and_third_calls_reveal_the_remaining_reserve_studies(
    fast_client: TestClient,
) -> None:
    first = fast_client.post("/api/studies/simulate").json()
    second = fast_client.post("/api/studies/simulate").json()
    third = fast_client.post("/api/studies/simulate").json()

    assert [first["id"], second["id"], third["id"]] == ["STU-002", "STU-003", "STU-006"]
    assert [first["patient_name"], second["patient_name"], third["patient_name"]] == [
        "Wei Zhang",
        "Priya Nair",
        "Liam O'Connor",
    ]


def test_fourth_call_falls_back_to_a_fabricated_study(fast_client: TestClient) -> None:
    for _ in range(3):
        fast_client.post("/api/studies/simulate")

    fourth = fast_client.post("/api/studies/simulate").json()

    assert fourth["id"] == "STU-007"
    assert fourth["id"] not in {"STU-002", "STU-003", "STU-006"}


def test_simulated_study_appears_in_worklist(fast_client: TestClient) -> None:
    fast_client.post("/api/studies/simulate")
    worklist = fast_client.get("/api/studies").json()

    assert len(worklist) == 4  # 3 initial + 1 revealed
    assert any(s["id"] == "STU-002" for s in worklist)
