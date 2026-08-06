"""
Worklist prioritization policy.

Implements the exact policy table from the UX Workflow & Trust Design doc:

| AI Assessment           | Confidence | Priority  |
|--------------------------|------------|-----------|
| Suspected ICH             | High       | Critical  |
| Suspected ICH             | Medium     | High      |
| No Suspicious Findings    | Medium     | Moderate  |
| No Suspicious Findings    | High       | Routine   |

The policy combines assessment with confidence rather than ranking positive
predictions alone - the objective is minimizing clinical risk, not just
surfacing "AI said yes" cases. Uncertainty (Medium confidence) always pushes
a study toward earlier review, never later, regardless of assessment.

Kept as pure functions (no I/O, no framework dependency) so they can be unit
tested directly and reused unchanged if a real AI engine replaces the
simulated one later.
"""

from typing import Literal

from app.core.config import CONFIDENCE_HIGH_THRESHOLD
from app.models.schemas import Assessment, Priority

ConfidenceTier = Literal["High", "Medium"]


def confidence_tier(confidence: float) -> ConfidenceTier:
    """Buckets a raw 0-1 confidence score into the two tiers the policy
    table is defined over."""
    return "High" if confidence >= CONFIDENCE_HIGH_THRESHOLD else "Medium"


_POLICY: dict[tuple[Assessment, ConfidenceTier], Priority] = {
    (Assessment.SUSPECTED_ICH, "High"): Priority.CRITICAL,
    (Assessment.SUSPECTED_ICH, "Medium"): Priority.HIGH,
    (Assessment.NO_SUSPICIOUS_FINDINGS, "Medium"): Priority.MODERATE,
    (Assessment.NO_SUSPICIOUS_FINDINGS, "High"): Priority.ROUTINE,
}


def determine_priority(assessment: Assessment, confidence: float) -> Priority:
    """Maps an AI assessment + confidence score to a worklist priority per
    the product's prioritization policy."""
    tier = confidence_tier(confidence)
    return _POLICY[(assessment, tier)]


# Sort order for the worklist: most urgent first. Studies without a priority
# yet (still Acquiring/Processing) sort after everything prioritized, per
# WL-03/WL-04 - a study only gets a position once AI processing completes.
_PRIORITY_RANK: dict[Priority, int] = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 1,
    Priority.MODERATE: 2,
    Priority.ROUTINE: 3,
}


def priority_sort_key(priority: Priority | None) -> int:
    """Sort key for ordering the worklist by urgency. Use as the `key=` for
    sorting a list of studies by `study.priority`."""
    if priority is None:
        return len(_PRIORITY_RANK)
    return _PRIORITY_RANK[priority]
