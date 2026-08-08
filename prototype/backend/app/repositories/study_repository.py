"""
In-memory study storage, seeded from JSON on startup.

This is the seam described in the implementation plan: routes and services
only ever talk to `StudyRepository`'s methods, never to the JSON file or the
underlying dict directly. Swapping this for a SQLite-backed implementation
later (Milestone 9+) means reimplementing this one class - nothing else in
the app needs to change.

Demo staging (Milestone 9): not every seeded study is visible right away.
`_seed_studies` holds all of them (the immutable source of truth, read but
never mutated after load); the live worklist (`_studies`) starts as just
INITIAL_DEMO_STUDY_IDS, and RESERVE_DEMO_STUDY_IDS are introduced one at a
time via `reveal_next_reserve_study()` ("Simulate New CT Study"), each with
its own real, pre-calibrated prediction rather than a fabricated one. "Reset
Demo" (`reset_demo_state()`) rebuilds the live worklist from `_seed_studies`
again, so it's always an exact, repeatable restore - never a mutation of the
seed data itself.

Not thread-safe beyond what Python's GIL gives us for free, which is fine
for a single-process MVP demo.
"""

import json
from datetime import datetime
from itertools import count
from pathlib import Path

from app.core.config import INITIAL_DEMO_STUDY_IDS, RESERVE_DEMO_STUDY_IDS
from app.core.prioritization import determine_priority, priority_sort_key
from app.models.schemas import Prediction, Study, StudyStatus

_SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "seed_studies.json"


class StudyRepository:
    def __init__(self, seed_file: Path = _SEED_FILE) -> None:
        self._seed_studies: dict[str, Study] = {}
        self._studies: dict[str, Study] = {}
        self._reserve_queue: list[str] = []
        self._id_counter = count(1)
        self._post_seed_counter_start = 1
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
            self._seed_studies[study.id] = study

            # Seed IDs look like "STU-001" - keep the id counter ahead of
            # them (all of them, not just the initially-visible ones) so
            # fabricated studies never collide with seed data.
            suffix = study.id.rsplit("-", 1)[-1]
            if suffix.isdigit():
                highest_seed_number = max(highest_seed_number, int(suffix))

        missing = [
            study_id
            for study_id in (*INITIAL_DEMO_STUDY_IDS, *RESERVE_DEMO_STUDY_IDS)
            if study_id not in self._seed_studies
        ]
        if missing:
            raise ValueError(
                f"app/core/config.py's demo study lists reference id(s) not "
                f"present in {seed_file.name}: {missing}"
            )

        self._post_seed_counter_start = highest_seed_number + 1
        self.reset_demo_state()

    def reset_demo_state(self) -> None:
        """"Reset Demo": restores the worklist to its initial three-study
        state (INITIAL_DEMO_STUDY_IDS), clears every simulated/fabricated
        study and re-queues the held-back real studies
        (RESERVE_DEMO_STUDY_IDS) so "Simulate New CT Study" reveals them
        again from the start. Only touches this in-memory demo state -
        never seed_studies.json, DICOM source files, or converted images."""
        self._studies = {
            study_id: self._seed_studies[study_id].model_copy(deep=True)
            for study_id in INITIAL_DEMO_STUDY_IDS
        }
        self._reserve_queue = list(RESERVE_DEMO_STUDY_IDS)
        self._id_counter = count(self._post_seed_counter_start)

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

    def get_seed_prediction(self, study_id: str) -> Prediction | None:
        """The real, pre-calibrated prediction for a seeded study (initial
        or reserve). Used to reveal a reserve study's actual AI result once
        its simulated workflow reaches Ready, instead of fabricating one
        (see app/services/study_workflow.py). None for ids with no seed
        data at all (a fully fabricated incoming study), which is the
        signal callers use to fall back to the AI engine."""
        seed = self._seed_studies.get(study_id)
        return seed.prediction if seed else None

    def reveal_next_reserve_study(self) -> Study | None:
        """Pops the next held-back real study (RESERVE_DEMO_STUDY_IDS) and
        adds it to the worklist in "Acquiring" status, using its real
        patient name/accession number/slice count - everything except the
        lifecycle fields (status/AI status/priority/prediction), which
        start blank exactly like a freshly-created fabricated study, and
        exam_datetime, bumped to now so it reads as a live incoming
        acquisition rather than showing its original seed timestamp. Its
        real prediction is revealed later via get_seed_prediction() once
        the simulated workflow reaches Ready. Returns None once the queue
        is empty, so callers can fall back to a fully fabricated study."""
        if not self._reserve_queue:
            return None
        study_id = self._reserve_queue.pop(0)
        seed = self._seed_studies[study_id]
        stub = seed.model_copy(
            update={
                "study_status": StudyStatus.ACQUIRING,
                "ai_status": None,
                "priority": None,
                "prediction": None,
                "exam_datetime": datetime.now(),
            }
        )
        self._studies[study_id] = stub
        return stub


# Module-level singleton, used as a FastAPI dependency (see app/api routes).
# A plain singleton - not a DB connection pool - so this is fine to share
# across requests within the single dev process.
_repository = StudyRepository()


def get_study_repository() -> StudyRepository:
    return _repository
