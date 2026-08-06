"""
Simulated implementation of the AI Triage Engine.

Seed studies (app/data/seed_studies.json) already carry their own baked-in
predictions and don't go through this engine. This implementation is only
invoked by the study workflow (Milestone 5) when a *new* study is created
via "Simulate New CT Study" and needs a prediction once it reaches the
AI Processing status.

Demo-shaping, not randomness for its own sake: the Design Spec's
demonstration script hinges on the first simulated study visibly jumping to
the top of the worklist, so the first call deterministically returns a
high-confidence Suspected ICH result (guaranteed Critical priority). Later
calls in the same session (if the demo is run through more than once) vary
randomly across all four policy outcomes so repeat clicks aren't identical.
"""

import random
from datetime import datetime

from app.models.schemas import Assessment, OverlayRegion, Prediction, Study
from app.services.ai_engine.base import AIEngine

# Plain-language locations for simulated ICH findings. Real values would come
# from wherever a real model reports its finding's anatomical location.
_HEMORRHAGE_LOCATIONS = [
    "Right parietal lobe",
    "Left frontal lobe",
    "Left temporal lobe",
    "Right occipital lobe",
    "Right basal ganglia",
]


class SimulatedAIEngine(AIEngine):
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._calls = 0

    def predict(self, study: Study) -> Prediction:
        self._calls += 1

        if self._calls == 1:
            # The demo's headline moment: guaranteed Suspected ICH, high
            # confidence -> Critical priority, so the study visibly jumps to
            # the top of the worklist.
            assessment = Assessment.SUSPECTED_ICH
            confidence = 0.91
        else:
            assessment = self._rng.choices(
                [Assessment.SUSPECTED_ICH, Assessment.NO_SUSPICIOUS_FINDINGS],
                weights=[0.4, 0.6],
            )[0]
            confidence = round(self._rng.uniform(0.55, 0.98), 2)

        if assessment == Assessment.SUSPECTED_ICH:
            hemorrhage_location = self._rng.choice(_HEMORRHAGE_LOCATIONS)
            overlay_region = self._build_overlay(study)
        else:
            hemorrhage_location = None
            overlay_region = None

        return Prediction(
            assessment=assessment,
            confidence=confidence,
            hemorrhage_location=hemorrhage_location,
            overlay_region=overlay_region,
            predicted_at=datetime.now(),
        )

    def _build_overlay(self, study: Study) -> OverlayRegion:
        """Places a plausible-looking highlight box on a middle-ish slice.
        Purely illustrative until real model output (or real images'
        geometry) replaces it."""
        slice_index = max(0, min(study.slice_count - 1, study.slice_count // 2))
        return OverlayRegion(
            slice_index=slice_index,
            x=round(self._rng.uniform(0.20, 0.60), 2),
            y=round(self._rng.uniform(0.20, 0.55), 2),
            width=0.18,
            height=0.16,
        )


# Module-level singleton + accessor, mirroring the repository pattern.
# --- AI ENGINE SWAP POINT -----------------------------------------------
# To use a real model instead of the simulation, implement AIEngine (e.g.
# in a new torch_engine.py) and change the line below to return an instance
# of it. Nothing in app/api or the frontend needs to change.
_engine: AIEngine = SimulatedAIEngine()


def get_ai_engine() -> AIEngine:
    return _engine
