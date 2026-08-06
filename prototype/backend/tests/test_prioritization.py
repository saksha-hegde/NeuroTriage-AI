"""Unit tests for the prioritization policy - the product's core business
rule, and the thing most worth protecting from silent regressions."""

import pytest

from app.core.prioritization import (
    confidence_tier,
    determine_priority,
    priority_sort_key,
)
from app.models.schemas import Assessment, Priority


class TestConfidenceTier:
    def test_at_or_above_threshold_is_high(self) -> None:
        assert confidence_tier(0.80) == "High"
        assert confidence_tier(0.99) == "High"
        assert confidence_tier(1.0) == "High"

    def test_below_threshold_is_medium(self) -> None:
        assert confidence_tier(0.79) == "Medium"
        assert confidence_tier(0.50) == "Medium"
        assert confidence_tier(0.0) == "Medium"


class TestDeterminePriority:
    """The full 2x2 policy table from the UX Workflow & Trust Design doc."""

    def test_suspected_ich_high_confidence_is_critical(self) -> None:
        assert (
            determine_priority(Assessment.SUSPECTED_ICH, 0.93) == Priority.CRITICAL
        )

    def test_suspected_ich_medium_confidence_is_high(self) -> None:
        assert determine_priority(Assessment.SUSPECTED_ICH, 0.62) == Priority.HIGH

    def test_no_suspicious_findings_medium_confidence_is_moderate(self) -> None:
        assert (
            determine_priority(Assessment.NO_SUSPICIOUS_FINDINGS, 0.58)
            == Priority.MODERATE
        )

    def test_no_suspicious_findings_high_confidence_is_routine(self) -> None:
        assert (
            determine_priority(Assessment.NO_SUSPICIOUS_FINDINGS, 0.95)
            == Priority.ROUTINE
        )

    @pytest.mark.parametrize(
        ("assessment", "confidence", "expected"),
        [
            (Assessment.SUSPECTED_ICH, 0.80, Priority.CRITICAL),  # boundary
            (Assessment.SUSPECTED_ICH, 0.7999, Priority.HIGH),  # just below
            (Assessment.NO_SUSPICIOUS_FINDINGS, 0.80, Priority.ROUTINE),
            (Assessment.NO_SUSPICIOUS_FINDINGS, 0.7999, Priority.MODERATE),
        ],
    )
    def test_threshold_boundary(self, assessment, confidence, expected) -> None:
        assert determine_priority(assessment, confidence) == expected


class TestPrioritySortKey:
    def test_orders_most_urgent_first(self) -> None:
        keys = [
            priority_sort_key(Priority.ROUTINE),
            priority_sort_key(Priority.MODERATE),
            priority_sort_key(Priority.HIGH),
            priority_sort_key(Priority.CRITICAL),
        ]
        assert keys == sorted(keys, reverse=True)

    def test_no_priority_sorts_after_everything(self) -> None:
        assert priority_sort_key(None) > priority_sort_key(Priority.ROUTINE)
