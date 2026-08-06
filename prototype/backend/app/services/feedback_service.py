"""
Turns a radiologist's Confirm/Override action into a recorded Feedback
entry and marks the study Reported.

FB-01/FB-02 (PRD): records the radiologist's final decision together with
the AI prediction it was made against - `prediction_snapshot` freezes the
prediction at decision time, independent of anything that happens to the
study afterward. FB-03: override decisions are stored the same way as
confirmations, distinguished only by `decision`.
"""

from datetime import datetime

from app.models.schemas import Feedback, FeedbackDecision, FeedbackRequest, Study, StudyStatus
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.study_repository import StudyRepository


class StudyNotReadyError(Exception):
    """Feedback was submitted before the study has an AI prediction."""


class FeedbackAlreadyRecordedError(Exception):
    """Feedback was submitted for a study that's already Reported - the
    Design Spec's workflow ends at Reported, no re-reporting in the MVP."""


def record_feedback(
    study: Study,
    request: FeedbackRequest,
    study_repo: StudyRepository,
    feedback_repo: FeedbackRepository,
) -> Feedback:
    if study.study_status == StudyStatus.REPORTED:
        raise FeedbackAlreadyRecordedError(f"Study '{study.id}' has already been reported")
    if study.prediction is None:
        raise StudyNotReadyError(f"Study '{study.id}' has no AI prediction yet")

    feedback = Feedback(
        id=feedback_repo.next_id(),
        study_id=study.id,
        prediction_snapshot=study.prediction,
        decision=FeedbackDecision(request.decision),
        overridden_assessment=request.overridden_assessment,
        recorded_at=datetime.now(),
    )
    feedback_repo.save(feedback)

    reported_study = study.model_copy(update={"study_status": StudyStatus.REPORTED})
    study_repo.save(reported_study)

    return feedback
