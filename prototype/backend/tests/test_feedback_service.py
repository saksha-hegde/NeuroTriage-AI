"""Tests for record_feedback - the business rules behind Confirm/Override."""

import pytest

from app.models.schemas import (
    Assessment,
    FeedbackDecision,
    FeedbackRequest,
    Study,
    StudyStatus,
)
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.study_repository import StudyRepository
from app.services.feedback_service import (
    FeedbackAlreadyRecordedError,
    StudyNotReadyError,
    record_feedback,
)


def make_repos() -> tuple[StudyRepository, FeedbackRepository]:
    return StudyRepository(), FeedbackRepository()


def test_confirm_records_feedback_and_reports_the_study() -> None:
    study_repo, feedback_repo = make_repos()
    study = study_repo.get_by_id("STU-001")  # Suspected ICH, Critical
    assert study is not None

    request = FeedbackRequest(decision=FeedbackDecision.CONFIRM)
    feedback = record_feedback(study, request, study_repo, feedback_repo)

    assert feedback.study_id == "STU-001"
    assert feedback.decision == FeedbackDecision.CONFIRM
    assert feedback.overridden_assessment is None
    assert feedback.prediction_snapshot == study.prediction

    updated = study_repo.get_by_id("STU-001")
    assert updated is not None
    assert updated.study_status == StudyStatus.REPORTED


def test_override_records_the_overridden_assessment() -> None:
    study_repo, feedback_repo = make_repos()
    study = study_repo.get_by_id("STU-001")  # AI said Suspected ICH
    assert study is not None

    request = FeedbackRequest(
        decision=FeedbackDecision.OVERRIDE,
        overridden_assessment=Assessment.NO_SUSPICIOUS_FINDINGS,
    )
    feedback = record_feedback(study, request, study_repo, feedback_repo)

    assert feedback.decision == FeedbackDecision.OVERRIDE
    assert feedback.overridden_assessment == Assessment.NO_SUSPICIOUS_FINDINGS


def test_feedback_is_retrievable_by_study_id() -> None:
    study_repo, feedback_repo = make_repos()
    study = study_repo.get_by_id("STU-001")
    assert study is not None

    recorded = record_feedback(
        study, FeedbackRequest(decision=FeedbackDecision.CONFIRM), study_repo, feedback_repo
    )

    fetched = feedback_repo.get_by_study_id("STU-001")
    assert fetched is not None
    assert fetched.id == recorded.id


def test_raises_when_study_has_no_prediction_yet() -> None:
    study_repo, feedback_repo = make_repos()
    unprocessed = Study(
        id="STU-TEST",
        patient_name="Test Patient",
        accession_number="ACC-TEST-0001",
        exam_datetime="2026-08-07T09:00:00",
        study_status=StudyStatus.ACQUIRING,
        slice_count=1,
    )

    with pytest.raises(StudyNotReadyError):
        record_feedback(
            unprocessed, FeedbackRequest(decision=FeedbackDecision.CONFIRM), study_repo, feedback_repo
        )


def test_raises_when_study_already_reported() -> None:
    study_repo, feedback_repo = make_repos()
    study = study_repo.get_by_id("STU-001")
    assert study is not None
    record_feedback(study, FeedbackRequest(decision=FeedbackDecision.CONFIRM), study_repo, feedback_repo)

    already_reported = study_repo.get_by_id("STU-001")
    assert already_reported is not None

    with pytest.raises(FeedbackAlreadyRecordedError):
        record_feedback(
            already_reported,
            FeedbackRequest(decision=FeedbackDecision.CONFIRM),
            study_repo,
            feedback_repo,
        )


class TestFeedbackRequestValidation:
    def test_confirm_without_overridden_assessment_is_valid(self) -> None:
        FeedbackRequest(decision=FeedbackDecision.CONFIRM)  # should not raise

    def test_override_without_overridden_assessment_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="overridden_assessment is required"):
            FeedbackRequest(decision=FeedbackDecision.OVERRIDE)

    def test_confirm_with_overridden_assessment_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be set"):
            FeedbackRequest(
                decision=FeedbackDecision.CONFIRM,
                overridden_assessment=Assessment.SUSPECTED_ICH,
            )

    def test_reject_is_not_an_accepted_decision(self) -> None:
        with pytest.raises(ValueError):
            FeedbackRequest(decision=FeedbackDecision.REJECT)
