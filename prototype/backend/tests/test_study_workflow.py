"""Tests for the Acquiring -> Completed/Processing -> Ready state machine,
exercised directly (not through the API) so the service logic is verified
independently of HTTP/background-task plumbing."""

import asyncio
import random

import app.services.study_workflow as workflow
from app.models.schemas import AIStatus, StudyStatus
from app.repositories.study_repository import StudyRepository
from app.services.ai_engine.simulated_engine import SimulatedAIEngine


def test_create_incoming_study_starts_in_acquiring() -> None:
    repo = StudyRepository()
    study = workflow.create_incoming_study(repo)

    assert study.study_status == StudyStatus.ACQUIRING
    assert study.ai_status is None
    assert study.priority is None
    assert study.prediction is None
    # It's saved immediately - visible in the worklist before any delay.
    assert repo.get_by_id(study.id) is not None


def test_create_incoming_study_uses_a_fresh_id_each_time() -> None:
    repo = StudyRepository()
    first = workflow.create_incoming_study(repo)
    second = workflow.create_incoming_study(repo)
    assert first.id != second.id


def test_full_workflow_reaches_ready_with_priority(monkeypatch) -> None:
    # Near-instant delays so the test doesn't actually wait ~5s.
    monkeypatch.setattr(workflow, "STUDY_ACQUIRING_SECONDS", 0.01)
    monkeypatch.setattr(workflow, "STUDY_AI_PROCESSING_SECONDS", 0.01)

    repo = StudyRepository()
    engine = SimulatedAIEngine(rng=random.Random(0))
    study = workflow.create_incoming_study(repo)

    asyncio.run(workflow.run_incoming_study_workflow(study.id, repo, engine))

    final = repo.get_by_id(study.id)
    assert final is not None
    assert final.study_status == StudyStatus.COMPLETED
    assert final.ai_status == AIStatus.READY
    assert final.priority is not None
    assert final.prediction is not None


def test_workflow_passes_through_processing_before_ready(monkeypatch) -> None:
    """Confirms the intermediate state (Completed + Processing) actually
    happens, rather than the study jumping straight from Acquiring to
    Ready."""
    monkeypatch.setattr(workflow, "STUDY_ACQUIRING_SECONDS", 0.05)
    monkeypatch.setattr(workflow, "STUDY_AI_PROCESSING_SECONDS", 0.05)

    repo = StudyRepository()
    engine = SimulatedAIEngine(rng=random.Random(0))
    study = workflow.create_incoming_study(repo)

    async def observe() -> None:
        task = asyncio.create_task(
            workflow.run_incoming_study_workflow(study.id, repo, engine)
        )

        await asyncio.sleep(0.08)  # after acquiring, mid-processing
        mid = repo.get_by_id(study.id)
        assert mid is not None
        assert mid.study_status == StudyStatus.COMPLETED
        assert mid.ai_status == AIStatus.PROCESSING
        assert mid.priority is None

        await task
        done = repo.get_by_id(study.id)
        assert done is not None
        assert done.ai_status == AIStatus.READY

    asyncio.run(observe())


def test_workflow_is_a_noop_if_study_was_removed(monkeypatch) -> None:
    """Defensive: shouldn't raise if the study somehow disappears between
    scheduling and the background task running."""
    monkeypatch.setattr(workflow, "STUDY_ACQUIRING_SECONDS", 0.01)
    monkeypatch.setattr(workflow, "STUDY_AI_PROCESSING_SECONDS", 0.01)

    repo = StudyRepository()
    engine = SimulatedAIEngine(rng=random.Random(0))

    asyncio.run(workflow.run_incoming_study_workflow("STU-does-not-exist", repo, engine))
    # No exception raised is the assertion.
