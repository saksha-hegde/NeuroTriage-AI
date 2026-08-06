"""Tests for StudyRepository: seed loading, derived priority, ordering, and
the id/save operations the simulation workflow will depend on."""

from app.core.prioritization import determine_priority
from app.models.schemas import Priority, Study, StudyStatus
from app.repositories.study_repository import StudyRepository


def make_repository() -> StudyRepository:
    # Fresh instance per test - avoid coupling to the app-wide singleton.
    return StudyRepository()


def test_loads_all_seed_studies() -> None:
    repo = make_repository()
    studies = repo.get_all()
    assert len(studies) == 6


def test_priority_is_derived_not_trusted_from_seed_file() -> None:
    repo = make_repository()
    for study in repo.get_all():
        assert study.prediction is not None
        expected = determine_priority(
            study.prediction.assessment, study.prediction.confidence
        )
        assert study.priority == expected


def test_worklist_is_sorted_most_urgent_first() -> None:
    repo = make_repository()
    priorities = [s.priority for s in repo.get_all()]
    rank = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MODERATE: 2, Priority.ROUTINE: 3}
    ranks = [rank[p] for p in priorities if p is not None]
    assert ranks == sorted(ranks)


def test_get_by_id_returns_matching_study() -> None:
    repo = make_repository()
    study = repo.get_by_id("STU-001")
    assert study is not None
    assert study.patient_name == "Jordan Ellis"


def test_get_by_id_returns_none_for_unknown_id() -> None:
    repo = make_repository()
    assert repo.get_by_id("does-not-exist") is None


def test_next_id_continues_after_seed_data() -> None:
    repo = make_repository()
    assert repo.next_id() == "STU-007"
    assert repo.next_id() == "STU-008"


def test_save_inserts_new_study() -> None:
    repo = make_repository()
    new_id = repo.next_id()
    new_study = Study(
        id=new_id,
        patient_name="Test Patient",
        accession_number="ACC-TEST-0001",
        exam_datetime="2026-08-07T09:00:00",
        study_status=StudyStatus.ACQUIRING,
        slice_count=1,
    )
    repo.save(new_study)
    assert repo.get_by_id(new_id) is not None
    assert len(repo.get_all()) == 7


def test_save_replaces_existing_study_in_place() -> None:
    repo = make_repository()
    study = repo.get_by_id("STU-001")
    assert study is not None
    updated = study.model_copy(update={"study_status": StudyStatus.REPORTED})
    repo.save(updated)

    assert repo.get_by_id("STU-001").study_status == StudyStatus.REPORTED
    assert len(repo.get_all()) == 6  # replaced, not duplicated
