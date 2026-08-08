"""
In-memory feedback storage. Same pattern as study_repository.py: a plain
dict behind a small class, swappable for a DB-backed implementation later
without touching anything upstream (FB-04: supports future model
improvement using captured feedback).
"""

from itertools import count

from app.models.schemas import Feedback


class FeedbackRepository:
    def __init__(self) -> None:
        self._feedback: dict[str, Feedback] = {}
        self._id_counter = count(1)

    def next_id(self) -> str:
        return f"FB-{next(self._id_counter):03d}"

    def save(self, feedback: Feedback) -> None:
        self._feedback[feedback.id] = feedback

    def get_by_study_id(self, study_id: str) -> Feedback | None:
        for feedback in self._feedback.values():
            if feedback.study_id == study_id:
                return feedback
        return None

    def get_all(self) -> list[Feedback]:
        return list(self._feedback.values())

    def reset(self) -> None:
        """"Reset Demo" (POST /studies/reset): clears every recorded
        Confirm/Override decision, restoring a clean feedback slate to go
        with the worklist's reset initial state."""
        self._feedback = {}
        self._id_counter = count(1)


# Module-level singleton, mirroring study_repository.py's pattern.
_repository = FeedbackRepository()


def get_feedback_repository() -> FeedbackRepository:
    return _repository
