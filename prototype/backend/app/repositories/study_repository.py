"""
In-memory study storage, seeded from JSON on startup.

This is the seam described in the implementation plan: routes and services
only ever talk to `StudyRepository`'s methods, never to the JSON file or the
underlying dict directly. Swapping this for a SQLite-backed implementation
later (Milestone 9+) means reimplementing this one class - nothing else in
the app needs to change.

Not thread-safe beyond what Python's GIL gives us for free, which is fine
for a single-process MVP demo.
"""

import json
from itertools import count
from pathlib import Path

from app.core.prioritization import determine_priority, priority_sort_key
from app.models.schemas import Study

_SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "seed_studies.json"


class StudyRepository:
    def __init__(self, seed_file: Path = _SEED_FILE) -> None:
        self._studies: dict[str, Study] = {}
        self._id_counter = count(1)
        self._load_seed(seed_file)

    def _load_seed(self, seed_file: Path) -> None:
        raw_studies = json.loads(seed_file.read_text(encoding="utf-8"))
        highest_seed_number = 0
        for raw in raw_studies:
            study = Study.model_validate(raw)
            if study.prediction is not None:
                study.priority = determine_priority(
                    study.prediction.assessment, study.prediction.confidence
                )
            self._studies[study.id] = study

            # Seed IDs look like "STU-001" - keep the id counter ahead of
            # them so simulated studies never collide with seed data.
            suffix = study.id.rsplit("-", 1)[-1]
            if suffix.isdigit():
                highest_seed_number = max(highest_seed_number, int(suffix))

        self._id_counter = count(highest_seed_number + 1)

    def next_id(self) -> str:
        return f"STU-{next(self._id_counter):03d}"

    def get_all(self) -> list[Study]:
        """Worklist order: most urgent priority first (WL-03/WL-04); studies
        with no priority yet (still being acquired/processed) sort last,
        ordered by exam time among themselves."""
        return sorted(
            self._studies.values(),
            key=lambda s: (priority_sort_key(s.priority), s.exam_datetime),
        )

    def get_by_id(self, study_id: str) -> Study | None:
        return self._studies.get(study_id)

    def save(self, study: Study) -> None:
        """Insert or replace. Callers (e.g. the workflow state machine) are
        expected to pass an updated copy of a Study they previously read."""
        self._studies[study.id] = study


# Module-level singleton, used as a FastAPI dependency (see app/api routes).
# A plain singleton - not a DB connection pool - so this is fine to share
# across requests within the single dev process.
_repository = StudyRepository()


def get_study_repository() -> StudyRepository:
    return _repository
