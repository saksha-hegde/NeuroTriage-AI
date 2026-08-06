"""Tests for the simulated AI Triage Engine."""

import random

from app.core.prioritization import determine_priority
from app.models.schemas import Assessment, Priority, Study, StudyStatus
from app.services.ai_engine.simulated_engine import SimulatedAIEngine


def make_study(slice_count: int = 30) -> Study:
    return Study(
        id="STU-TEST",
        patient_name="Test Patient",
        accession_number="ACC-TEST-0001",
        exam_datetime="2026-08-07T09:00:00",
        study_status=StudyStatus.COMPLETED,
        slice_count=slice_count,
    )


def test_first_prediction_is_the_demo_headline_case() -> None:
    """The first simulated study must land on Critical so the demo's
    reprioritization moment (Design Spec demonstration script step 5) is
    guaranteed to happen, not left to chance."""
    engine = SimulatedAIEngine(rng=random.Random(0))
    prediction = engine.predict(make_study())

    assert prediction.assessment == Assessment.SUSPECTED_ICH
    assert determine_priority(prediction.assessment, prediction.confidence) == (
        Priority.CRITICAL
    )
    assert prediction.hemorrhage_location is not None
    assert prediction.overlay_region is not None


def test_ich_predictions_always_include_location_and_overlay() -> None:
    engine = SimulatedAIEngine(rng=random.Random(1))
    for _ in range(20):
        prediction = engine.predict(make_study())
        if prediction.assessment == Assessment.SUSPECTED_ICH:
            assert prediction.hemorrhage_location is not None
            assert prediction.overlay_region is not None
        else:
            assert prediction.hemorrhage_location is None
            assert prediction.overlay_region is None


def test_overlay_slice_index_is_within_study_bounds() -> None:
    engine = SimulatedAIEngine(rng=random.Random(0))
    study = make_study(slice_count=10)
    prediction = engine.predict(study)  # first call is always ICH

    assert prediction.overlay_region is not None
    assert 0 <= prediction.overlay_region.slice_index < study.slice_count


def test_same_seed_is_deterministic() -> None:
    engine_a = SimulatedAIEngine(rng=random.Random(42))
    engine_b = SimulatedAIEngine(rng=random.Random(42))
    study = make_study()

    for _ in range(5):
        pred_a = engine_a.predict(study)
        pred_b = engine_b.predict(study)
        assert pred_a.assessment == pred_b.assessment
        assert pred_a.confidence == pred_b.confidence
