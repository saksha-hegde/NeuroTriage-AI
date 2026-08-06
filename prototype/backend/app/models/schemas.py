"""
Domain schemas shared across the API, services, and repositories.

These mirror the vocabulary of the PRD and MVP Prototype Design Specification
directly (status names, priority labels) so the API payloads read the same
way the product documents do, and so the frontend's TypeScript types
(src/types/) can be a near 1:1 mirror.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class StudyStatus(str, Enum):
    """Design Spec section 3: Acquiring, Completed, Reported."""

    ACQUIRING = "Acquiring"
    COMPLETED = "Completed"
    REPORTED = "Reported"


class AIStatus(str, Enum):
    """Design Spec section 3: Processing, Ready. Absent (None) until a study
    reaches StudyStatus.COMPLETED - AI has nothing to process before then."""

    PROCESSING = "Processing"
    READY = "Ready"


class Assessment(str, Enum):
    """The two AI outcomes defined in the UX Workflow & Trust Design policy
    table."""

    SUSPECTED_ICH = "Suspected ICH"
    NO_SUSPICIOUS_FINDINGS = "No Suspicious Findings"


class Priority(str, Enum):
    """The four worklist priorities from the UX Workflow & Trust Design
    prioritization policy table, ordered most to least urgent."""

    CRITICAL = "Critical"
    HIGH = "High"
    MODERATE = "Moderate"
    ROUTINE = "Routine"


class FeedbackDecision(str, Enum):
    """Radiologist actions on the Reading screen.

    REJECT is modeled here as a reserved value for forward compatibility with
    the UX doc's Confirm/Override/Reject vocabulary, but the MVP only wires
    up CONFIRM and OVERRIDE (see the implementation plan) - no API/UI path
    produces REJECT yet.
    """

    CONFIRM = "Confirm"
    OVERRIDE = "Override"
    REJECT = "Reject"  # reserved - not used by the MVP


class OverlayRegion(BaseModel):
    """A simulated explainability highlight over one CT slice.

    Coordinates are fractions (0-1) of the image's width/height rather than
    pixels, so the frontend can position the overlay without knowing the
    real image's pixel dimensions ahead of time - important once real
    (variably-sized) CT slices replace anything generated.
    """

    slice_index: int = Field(..., ge=0, description="0-based index of the slice this overlay belongs to")
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)
    width: float = Field(..., gt=0, le=1)
    height: float = Field(..., gt=0, le=1)


class Prediction(BaseModel):
    """The AI Triage Engine's output for one study. Produced by whatever
    implements app.services.ai_engine.base.AIEngine - simulated today, a
    real model later, with this shape unchanged either way."""

    assessment: Assessment
    confidence: float = Field(..., ge=0, le=1)
    hemorrhage_location: str | None = Field(
        default=None,
        description="Plain-language location, e.g. 'Right temporal lobe'. "
        "None when assessment is NO_SUSPICIOUS_FINDINGS.",
    )
    overlay_region: OverlayRegion | None = Field(
        default=None,
        description="None when assessment is NO_SUSPICIOUS_FINDINGS.",
    )
    predicted_at: datetime


class Study(BaseModel):
    """A CT Brain study as it appears in the worklist and reading screen."""

    id: str
    patient_name: str
    accession_number: str
    study_description: str = "CT Brain W/O Contrast"
    exam_datetime: datetime

    study_status: StudyStatus
    ai_status: AIStatus | None = None
    priority: Priority | None = None
    prediction: Prediction | None = None

    slice_count: int = Field(..., gt=0)


class Feedback(BaseModel):
    """A radiologist's recorded decision on a study's AI prediction.

    Links the decision back to the exact prediction it was made against
    (FB-02 in the PRD: 'record AI predictions for comparison'), independent
    of whatever the prediction looks like later.
    """

    id: str
    study_id: str
    prediction_snapshot: Prediction
    decision: FeedbackDecision
    overridden_assessment: Assessment | None = Field(
        default=None,
        description="Set when decision is OVERRIDE: what the radiologist "
        "determined instead of the AI's assessment.",
    )
    recorded_at: datetime


class FeedbackRequest(BaseModel):
    """Request body for POST /studies/{id}/feedback.

    Restricted to the two actions the MVP implements. FeedbackDecision.REJECT
    exists in the domain enum for forward compatibility but is intentionally
    not a valid value here - there is no UI/API path to it in the MVP.
    """

    decision: Literal[FeedbackDecision.CONFIRM, FeedbackDecision.OVERRIDE]
    overridden_assessment: Assessment | None = None

    @model_validator(mode="after")
    def _validate_override_has_assessment(self) -> FeedbackRequest:
        if self.decision == FeedbackDecision.OVERRIDE and self.overridden_assessment is None:
            raise ValueError("overridden_assessment is required when decision is 'Override'")
        if self.decision == FeedbackDecision.CONFIRM and self.overridden_assessment is not None:
            raise ValueError("overridden_assessment must not be set when decision is 'Confirm'")
        return self
