"""
Study-related API routes.

Kept thin: routes validate/translate HTTP <-> domain objects and delegate to
the repository/services. No business logic lives here (see
app/core/prioritization.py and app/services/).
"""

import io

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response
from PIL import Image

from app.models.schemas import Feedback, FeedbackRequest, Study
from app.repositories.feedback_repository import FeedbackRepository, get_feedback_repository
from app.repositories.study_repository import StudyRepository, get_study_repository
from app.services.ai_engine.base import AIEngine
from app.services.ai_engine.simulated_engine import get_ai_engine
from app.services.feedback_service import (
    FeedbackAlreadyRecordedError,
    StudyNotReadyError,
    record_feedback,
)
from app.services.image_store import get_dicom_default_window, get_raw_slice_hu
from app.services.study_workflow import run_incoming_study_workflow, start_incoming_study
from app.services.windowing import PresetName, apply_window, resolve_preset

router = APIRouter(prefix="/studies", tags=["studies"])


@router.get("/ping")
def ping() -> dict[str, str]:
    """Trivial route so the router wiring can be verified end-to-end."""
    return {"status": "studies router is wired up"}


@router.get("", response_model=list[Study])
def list_studies(
    repo: StudyRepository = Depends(get_study_repository),
) -> list[Study]:
    """The worklist (WL-01): every study, ordered most urgent first."""
    return repo.get_all()


@router.post("/simulate", response_model=Study, status_code=201)
def simulate_new_study(
    background_tasks: BackgroundTasks,
    repo: StudyRepository = Depends(get_study_repository),
    ai_engine: AIEngine = Depends(get_ai_engine),
) -> Study:
    """Design Spec section 3: creates a new study that progresses through
    Acquiring -> Completed -> AI Processing -> Ready and is then
    automatically reprioritized. Returns immediately with the study in
    "Acquiring" status; the rest of the workflow runs in the background
    (see app/services/study_workflow.py) and is observed by polling
    GET /studies or GET /studies/{id}.
    """
    study = start_incoming_study(repo)
    background_tasks.add_task(run_incoming_study_workflow, study.id, repo, ai_engine)
    return study


@router.post("/reset", response_model=list[Study])
def reset_demo(
    study_repo: StudyRepository = Depends(get_study_repository),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository),
) -> list[Study]:
    """"Reset Demo": restores the worklist to its initial three-study state
    (app/core/config.py's INITIAL_DEMO_STUDY_IDS), clears every simulated/
    fabricated study and recorded Confirm/Override decision, and re-queues
    the held-back real studies so "Simulate New CT Study" reveals them
    again from the start. Never touches seed_studies.json, DICOM source
    files, or converted images - only in-memory demo state (see
    StudyRepository.reset_demo_state / FeedbackRepository.reset)."""
    study_repo.reset_demo_state()
    feedback_repo.reset()
    return study_repo.get_all()


@router.get("/{study_id}", response_model=Study)
def get_study(
    study_id: str,
    repo: StudyRepository = Depends(get_study_repository),
) -> Study:
    """A single study's detail, for the Reading Experience screen."""
    study = repo.get_by_id(study_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Study '{study_id}' not found")
    return study


@router.get("/{study_id}/slices/{slice_index}")
def get_slice_image(
    study_id: str,
    slice_index: int,
    preset: PresetName = "brain",
    repo: StudyRepository = Depends(get_study_repository),
) -> Response:
    """One CT slice image, windowed for display (RD-01: display the CT study
    selected from the worklist). Converted ahead of time by
    scripts/convert_dicom.py into lossless per-slice HU data - this endpoint
    never touches DICOM, but it does apply the requested window/level
    (`preset`: "brain" | "blood" | "dicom", default "brain") to that
    preserved data on every call, so window/level can change without ever
    re-converting the source DICOM. See app/services/windowing.py."""
    study = repo.get_by_id(study_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Study '{study_id}' not found")
    if not (0 <= slice_index < study.slice_count):
        raise HTTPException(
            status_code=404,
            detail=f"Slice {slice_index} out of range for '{study_id}' "
            f"(0-{study.slice_count - 1})",
        )

    hu = get_raw_slice_hu(study_id, slice_index)
    if hu is None:
        raise HTTPException(
            status_code=404,
            detail="Image not available yet - see backend/app/data/README.md "
            "to add real CT images for this study.",
        )

    dicom_default = get_dicom_default_window(study_id) if preset == "dicom" else None
    windowed = apply_window(hu, resolve_preset(preset, dicom_default))

    buffer = io.BytesIO()
    Image.fromarray(windowed, mode="L").save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")


@router.post("/{study_id}/feedback", response_model=Feedback, status_code=201)
def submit_feedback(
    study_id: str,
    request: FeedbackRequest,
    study_repo: StudyRepository = Depends(get_study_repository),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository),
) -> Feedback:
    """RD-05/FB-01: the radiologist confirms or overrides the AI
    recommendation. Records the decision and moves the study to Reported -
    see app/services/feedback_service.py for the business rules."""
    study = study_repo.get_by_id(study_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Study '{study_id}' not found")

    try:
        return record_feedback(study, request, study_repo, feedback_repo)
    except StudyNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FeedbackAlreadyRecordedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
