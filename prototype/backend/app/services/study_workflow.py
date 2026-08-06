"""
The simulated study acquisition/processing state machine.

Implements the Design Spec's Prototype Workflow exactly:

    Simulate New CT Study -> Study Status: Acquiring
    -> Study Status: Completed + AI Status: Processing
    -> AI Status: Ready -> Priority Assigned -> Study Moves to Top

Runs as a FastAPI background task so `POST /studies/simulate` can return
immediately (the new study appears in the worklist right away, in
"Acquiring" status) while the transitions happen on their own schedule.
Timing constants live in app/core/config.py so they're easy to tune without
touching this logic.
"""

import asyncio
from datetime import datetime

from app.core.config import STUDY_ACQUIRING_SECONDS, STUDY_AI_PROCESSING_SECONDS
from app.core.prioritization import determine_priority
from app.models.schemas import Study, StudyStatus, AIStatus
from app.repositories.study_repository import StudyRepository
from app.services.ai_engine.base import AIEngine

# A small rotating cast for simulated incoming studies - distinct from the
# seeded worklist's patients so it's obvious which study is the new one.
_INCOMING_PATIENTS = [
    "Elena Kowalski",
    "David Okafor",
    "Sana Malik",
    "Tomás Rivera",
    "Grace Lindqvist",
]


def create_incoming_study(repo: StudyRepository) -> Study:
    """Creates a new study in "Acquiring" status and saves it immediately,
    so it shows up in the worklist before any simulated delay elapses."""
    study_id = repo.next_id()
    # Cycle through the cast deterministically by id number rather than
    # randomly, so which patient appears next is predictable across a demo.
    seq = int(study_id.rsplit("-", 1)[-1])
    patient_name = _INCOMING_PATIENTS[(seq - 1) % len(_INCOMING_PATIENTS)]

    study = Study(
        id=study_id,
        patient_name=patient_name,
        accession_number=f"ACC-{datetime.now():%Y%m%d}-{study_id.rsplit('-', 1)[-1]}",
        exam_datetime=datetime.now(),
        study_status=StudyStatus.ACQUIRING,
        ai_status=None,
        priority=None,
        prediction=None,
        slice_count=30,  # placeholder until real image sets are wired in (Milestone 6)
    )
    repo.save(study)
    return study


async def run_incoming_study_workflow(
    study_id: str, repo: StudyRepository, ai_engine: AIEngine
) -> None:
    """Advances a study through Acquiring -> Completed/Processing -> Ready,
    persisting each transition so polling clients see it happen in stages -
    rather than the study appearing to teleport straight to "Ready".
    """
    await asyncio.sleep(STUDY_ACQUIRING_SECONDS)

    study = repo.get_by_id(study_id)
    if study is None:
        return  # defensive: nothing to advance if it's gone
    study = study.model_copy(
        update={"study_status": StudyStatus.COMPLETED, "ai_status": AIStatus.PROCESSING}
    )
    repo.save(study)

    await asyncio.sleep(STUDY_AI_PROCESSING_SECONDS)

    study = repo.get_by_id(study_id)
    if study is None:
        return
    prediction = ai_engine.predict(study)
    priority = determine_priority(prediction.assessment, prediction.confidence)
    study = study.model_copy(
        update={"ai_status": AIStatus.READY, "priority": priority, "prediction": prediction}
    )
    repo.save(study)
