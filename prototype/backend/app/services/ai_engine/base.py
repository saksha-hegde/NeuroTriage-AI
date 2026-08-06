"""
The AI Triage Engine's contract.

This is the single piece of architecture the MVP Prototype Design
Specification requires: "The architecture should support replacing
[simulated outputs] with a real inference engine later without changing the
UI." Every caller (the study workflow, the API) depends on this interface,
never on `SimulatedAIEngine` directly - so a future `TorchAIEngine` (or
whatever wraps a real PyTorch/MONAI model) is a second implementation of
`predict`, swapped in at `get_ai_engine()` (see simulated_engine.py), with
no changes anywhere upstream.
"""

from abc import ABC, abstractmethod

from app.models.schemas import Prediction, Study


class AIEngine(ABC):
    @abstractmethod
    def predict(self, study: Study) -> Prediction:
        """Analyze a study and return the AI Triage Engine's output.

        Implementations own everything about *how* the prediction is
        produced (simulated, rule-based, or a real model's inference call).
        Callers only ever depend on this signature and on `Prediction`'s
        shape (app/models/schemas.py).
        """
        raise NotImplementedError
