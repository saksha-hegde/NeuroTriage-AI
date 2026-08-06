"""
Study-related API routes.

Kept thin: routes validate/translate HTTP <-> domain objects and delegate to
the repository/services. No business logic lives here (see
app/core/prioritization.py and app/services/).
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

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
from app.services.image_store import get_slice_path
from app.services.study_workflow import create_incoming_study, run_incoming_study_workflow

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
    study = create_incoming_study(repo)
    background_tasks.add_task(run_incoming_study_workflow, study.id, repo, ai_engine)
    return study


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
    repo: StudyRepository = Depends(get_study_repository),
) -> FileResponse:
    """One CT slice image (RD-01: display the CT study selected from the
    worklist). Converted ahead of time by scripts/convert_dicom.py - this
    endpoint only ever reads a PNG off disk, it never touches DICOM."""
    study = repo.get_by_id(study_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Study '{study_id}' not found")
    if not (0 <= slice_index < study.slice_count):
        raise HTTPException(
            status_code=404,
            detail=f"Slice {slice_index} out of range for '{study_id}' "
            f"(0-{study.slice_count - 1})",
        )

    path = get_slice_path(study_id, slice_index)
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Image not available yet - see backend/app/data/README.md "
            "to add real CT images for this study.",
        )
    return FileResponse(path, media_type="image/png")


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
