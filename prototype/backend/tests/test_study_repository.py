"""Tests for StudyRepository: seed loading, derived priority, ordering, the
id/save operations the simulation workflow depends on, and the Milestone 9
demo-staging behavior (initial three-study state, reserve-study reveal,
Reset Demo)."""

from app.core.config import INITIAL_DEMO_STUDY_IDS, RESERVE_DEMO_STUDY_IDS
from app.core.prioritization import determine_priority
from app.models.schemas import Priority, Study, StudyStatus
from app.repositories.study_repository import StudyRepository


def make_repository() -> StudyRepository:
    # Fresh instance per test - avoid coupling to the app-wide singleton.
    return StudyRepository()


def test_loads_only_the_initial_three_studies() -> None:
    repo = make_repository()
    studies = repo.get_all()
    assert len(studies) == 3
    assert {s.id for s in studies} == set(INITIAL_DEMO_STUDY_IDS)


def test_initial_worklist_matches_the_demo_script() -> None:
    """Jordan Ellis - Critical, Ahmed Farouk - Moderate, Maria Castillo -
    Routine - the exact three-study state Reset Demo must also restore."""
    repo = make_repository()
    by_id = {s.id: s for s in repo.get_all()}
    assert by_id["STU-001"].patient_name == "Jordan Ellis"
    assert by_id["STU-001"].priority == Priority.CRITICAL
    assert by_id["STU-004"].patient_name == "Ahmed Farouk"
    assert by_id["STU-004"].priority == Priority.MODERATE
    assert by_id["STU-005"].patient_name == "Maria Castillo"
    assert by_id["STU-005"].priority == Priority.ROUTINE


def test_reserve_studies_are_not_visible_initially() -> None:
    repo = make_repository()
    for study_id in RESERVE_DEMO_STUDY_IDS:
        assert repo.get_by_id(study_id) is None
    assert all(s.id not in RESERVE_DEMO_STUDY_IDS for s in repo.get_all())


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
    assert make_repository().get_by_id("does-not-exist") is None


def test_next_id_continues_after_all_seed_data_not_just_initial() -> None:
    # Highest seeded id is STU-006 even though only 3 studies are initially
    # visible - the counter must still skip past all 6 seed ids.
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
    assert len(repo.get_all()) == 4  # 3 initial + 1 inserted


def test_save_replaces_existing_study_in_place() -> None:
    repo = make_repository()
    study = repo.get_by_id("STU-001")
    assert study is not None
    updated = study.model_copy(update={"study_status": StudyStatus.REPORTED})
    repo.save(updated)

    assert repo.get_by_id("STU-001").study_status == StudyStatus.REPORTED
    assert len(repo.get_all()) == 3  # replaced, not duplicated


class TestReserveStudyReveal:
    def test_reveals_in_configured_order(self) -> None:
        repo = make_repository()
        revealed_ids = [repo.reveal_next_reserve_study().id for _ in RESERVE_DEMO_STUDY_IDS]
        assert revealed_ids == RESERVE_DEMO_STUDY_IDS

    def test_returns_none_once_exhausted(self) -> None:
        repo = make_repository()
        for _ in RESERVE_DEMO_STUDY_IDS:
            repo.reveal_next_reserve_study()
        assert repo.reveal_next_reserve_study() is None

    def test_revealed_study_starts_in_acquiring_with_no_prediction_yet(self) -> None:
        repo = make_repository()
        revealed = repo.reveal_next_reserve_study()
        assert revealed.study_status == StudyStatus.ACQUIRING
        assert revealed.ai_status is None
        assert revealed.priority is None
        assert revealed.prediction is None

    def test_revealed_study_keeps_its_real_identity(self) -> None:
        repo = make_repository()
        revealed = repo.reveal_next_reserve_study()
        assert revealed.id == "STU-002"
        assert revealed.patient_name == "Wei Zhang"
        assert revealed.slice_count == 92  # the real converted slice count

    def test_revealed_study_is_immediately_visible_in_worklist(self) -> None:
        repo = make_repository()
        revealed = repo.reveal_next_reserve_study()
        assert repo.get_by_id(revealed.id) is not None
        assert any(s.id == revealed.id for s in repo.get_all())


class TestSeedPrediction:
    def test_returns_the_real_calibrated_prediction_for_a_reserve_study(self) -> None:
        repo = make_repository()
        prediction = repo.get_seed_prediction("STU-002")
        assert prediction is not None
        assert prediction.assessment == "Suspected ICH"
        assert prediction.confidence == 0.88
        assert prediction.hemorrhage_location == "Left frontal lobe"
        assert prediction.overlay_region.slice_index == 35

    def test_returns_none_for_an_id_with_no_seed_data(self) -> None:
        repo = make_repository()
        assert repo.get_seed_prediction("STU-999") is None


class TestResetDemoState:
    def test_restores_exactly_the_initial_three_studies(self) -> None:
        repo = make_repository()
        repo.reveal_next_reserve_study()
        repo.reveal_next_reserve_study()
        new_id = repo.next_id()
        repo.save(
            Study(
                id=new_id,
                patient_name="Fabricated Patient",
                accession_number="ACC-TEST-0001",
                exam_datetime="2026-08-07T09:00:00",
                study_status=StudyStatus.ACQUIRING,
                slice_count=1,
            )
        )
        updated = repo.get_by_id("STU-001").model_copy(
            update={"study_status": StudyStatus.REPORTED}
        )
        repo.save(updated)

        repo.reset_demo_state()

        assert {s.id for s in repo.get_all()} == set(INITIAL_DEMO_STUDY_IDS)
        assert repo.get_by_id("STU-001").study_status == StudyStatus.COMPLETED

    def test_re_queues_reserve_studies_for_another_reveal_pass(self) -> None:
        repo = make_repository()
        for _ in RESERVE_DEMO_STUDY_IDS:
            repo.reveal_next_reserve_study()
        assert repo.reveal_next_reserve_study() is None  # queue exhausted

        repo.reset_demo_state()

        assert repo.reveal_next_reserve_study().id == RESERVE_DEMO_STUDY_IDS[0]

    def test_resets_the_id_counter(self) -> None:
        repo = make_repository()
        repo.next_id()
        repo.next_id()  # counter now ahead of STU-007

        repo.reset_demo_state()

        assert repo.next_id() == "STU-007"

    def test_does_not_mutate_seed_data_itself(self) -> None:
        """A study revealed and then reset shouldn't leave its live-copy
        mutations (e.g. exam_datetime bumped to "now" on reveal) bleeding
        into the seed data reset rebuilds from."""
        repo = make_repository()
        repo.reveal_next_reserve_study()  # mutates the live copy of STU-002
        repo.reset_demo_state()

        re_revealed = repo.reveal_next_reserve_study()
        assert re_revealed.slice_count == 92  # still the real seeded value
