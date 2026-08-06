"""API-level tests for POST /studies/{id}/feedback."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import Study, StudyStatus
from app.repositories.feedback_repository import FeedbackRepository, get_feedback_repository
from app.repositories.study_repository import StudyRepository, get_study_repository


@pytest.fixture()
def isolated_repo():
    return StudyRepository()


@pytest.fixture()
def isolated_client(isolated_repo: StudyRepository):
    # Isolated instances (not the app's shared singletons) so these tests -
    # which mutate study status to Reported - can't affect other test files.
    feedback_repo = FeedbackRepository()
    app.dependency_overrides[get_study_repository] = lambda: isolated_repo
    app.dependency_overrides[get_feedback_repository] = lambda: feedback_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_confirm_reports_the_study(isolated_client: TestClient) -> None:
    response = isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Confirm"})
    assert response.status_code == 201
    body = response.json()
    assert body["decision"] == "Confirm"
    assert body["study_id"] == "STU-001"

    study = isolated_client.get("/api/studies/STU-001").json()
    assert study["study_status"] == "Reported"


def test_override_requires_overridden_assessment(isolated_client: TestClient) -> None:
    response = isolated_client.post(
        "/api/studies/STU-001/feedback",
        json={"decision": "Override", "overridden_assessment": "No Suspicious Findings"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["decision"] == "Override"
    assert body["overridden_assessment"] == "No Suspicious Findings"


def test_override_without_assessment_is_rejected(isolated_client: TestClient) -> None:
    response = isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Override"})
    assert response.status_code == 422


def test_reject_decision_is_rejected(isolated_client: TestClient) -> None:
    response = isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Reject"})
    assert response.status_code == 422


def test_404_for_unknown_study(isolated_client: TestClient) -> None:
    response = isolated_client.post(
        "/api/studies/does-not-exist/feedback", json={"decision": "Confirm"}
    )
    assert response.status_code == 404


def test_409_when_study_not_ready(
    isolated_client: TestClient, isolated_repo: StudyRepository
) -> None:
    # A study still Acquiring has no prediction yet - seeded directly rather
    # than via /simulate, since TestClient runs the simulate workflow's
    # background task to completion before returning, so by the time a
    # response comes back the study would already be Ready.
    unprocessed = Study(
        id="STU-UNREADY",
        patient_name="Test Patient",
        accession_number="ACC-TEST-0001",
        exam_datetime="2026-08-07T09:00:00",
        study_status=StudyStatus.ACQUIRING,
        slice_count=1,
    )
    isolated_repo.save(unprocessed)

    response = isolated_client.post(
        "/api/studies/STU-UNREADY/feedback", json={"decision": "Confirm"}
    )
    assert response.status_code == 409


def test_409_when_already_reported(isolated_client: TestClient) -> None:
    isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Confirm"})
    response = isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Confirm"})
    assert response.status_code == 409


def test_worklist_reflects_reported_status(isolated_client: TestClient) -> None:
    isolated_client.post("/api/studies/STU-001/feedback", json={"decision": "Confirm"})
    worklist = isolated_client.get("/api/studies").json()
    stu_001 = next(s for s in worklist if s["id"] == "STU-001")
    assert stu_001["study_status"] == "Reported"
