# NeuroTriage AI — Prototype

MVP prototype demonstrating an AI-assisted emergency stroke triage workflow: a
simulated PACS worklist that automatically prioritizes suspected intracranial
hemorrhage (ICH) studies, and a reading screen where the radiologist reviews
AI findings and confirms or overrides them.

This prototype simulates AI inference behind a swappable interface (see
[Architecture](#architecture)) — it demonstrates the **workflow**, not a
production AI model. See `../Appendix/DesignSpecification/`,
`../Appendix/PRD.md`, and `../Appendix/UX_Workflow_Trust_Design/` for the
governing product documents.

> Build status: Milestones 1-7 complete (scaffolding; domain model & seed
> data; simulated AI Triage Engine; Worklist API + Screen 1; Simulate New
> Study workflow; Reading Experience; Confirm/Override + feedback capture),
> plus all six real DICOM studies converted and their AI overlays
> calibrated, and Milestone 9's Reset Demo / Jump to Finding / staged
> three-study reveal implemented and manually verified end-to-end. See
> [Implementation milestones](#implementation-milestones) below.

---

## Prerequisites

- **Node.js 18+** and npm (frontend)
- **Python 3.11+** (backend)

## Setup

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend (separate terminal)
cd frontend
npm install
```

## Running

```bash
# Terminal 1 — backend (http://localhost:8000)
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (http://localhost:5173)
cd frontend
npm run dev
```

Open http://localhost:5173 for the worklist. It starts with three studies
(Jordan Ellis - Critical, Ahmed Farouk - Moderate, Maria Castillo - Routine).
Click a row to open the Reading Experience for that study, or "Simulate New
CT Study" to watch a study move through Acquiring → Processing → Ready and
reprioritize live - the first three clicks reveal the three remaining real
DICOM studies (Wei Zhang, Priya Nair, Liam O'Connor) with their own
pre-calibrated predictions; further clicks fabricate additional demo
patients. "Reset Demo" (with a confirmation step) restores the worklist to
its exact starting three-study state - it only resets in-memory demo state,
never your DICOM source files or converted images. In the Reading
Experience, "Jump to Finding" jumps straight to the AI's highlighted slice
and enables the overlay. API docs are auto-generated at
http://localhost:8000/docs.

## Testing

```bash
cd backend
pytest
```

---

## Real CT images

All six studies' real anonymized DICOM have been converted and their AI
overlays hand-calibrated against the actual images (see
`backend/app/data/README.md` and the windowing details below). The Reading
Experience still falls back to an honest "CT image not available yet" state
for any study with no converted images, rather than a broken viewer — so if
you replace or add DICOM later, nothing breaks in the meantime:

```bash
cd backend
mkdir -p app/data/dicom_source/STU-001   # one folder per study you're populating
# copy that study's anonymized .dcm files into it (extensionless files are
# also picked up if they're valid DICOM), then repeat for other study ids

python -m scripts.convert_dicom
```

This converts each study's slices into lossless per-slice Hounsfield-unit
PNGs in `app/data/images/{study_id}/` and automatically updates
`slice_count` in `seed_studies.json`. For any *new or changed* Suspected ICH
study, review the converted images (cycle window presets in the viewer) and
adjust `overlay_region` (x/y/width/height/slice_index) by hand in
`seed_studies.json` so the highlighted region lines up with what's visible —
that's not something conversion can infer.

---

## Architecture

Three subsystems, matching the PRD:

- **AI Triage Engine** (`backend/app/services/ai_engine/`) — a single
  `AIEngine` interface (`predict(study) -> Prediction`). The current
  implementation (`simulated_engine.py`) returns seed-driven results. A real
  PyTorch/MONAI model becomes a second implementation of the same interface,
  swapped in via config — **no frontend or API changes required**.
- **PACS Worklist** (frontend `WorklistPage` + `GET /api/studies`) — displays
  and auto-reprioritizes studies as AI processing completes.
- **Reading Experience** (frontend `ReadingPage` + study detail/feedback
  endpoints) — CT slice viewer, AI assessment panel, Confirm/Override. Real
  DICOM is converted ahead of time (`scripts/convert_dicom.py`) into
  lossless per-slice Hounsfield-unit PNGs, so the viewer and API only ever
  deal with static images, never DICOM directly. Window/level (Brain /
  Blood-ICH / DICOM-default presets) is applied per-request from that
  preserved data (`app/services/windowing.py`), so it can change without
  re-converting.

Data (v1): seeded from JSON, held in in-memory repository classes
(`backend/app/repositories/`). No database yet — repositories are the seam
where SQLite would be introduced later without touching routes or the
frontend.

**Demo staging** (`app/core/config.py`'s `INITIAL_DEMO_STUDY_IDS` /
`RESERVE_DEMO_STUDY_IDS`): `StudyRepository` loads all seed studies but only
exposes the initial three in the worklist; the other three are held in
reserve and revealed one at a time - with their own real, pre-calibrated
prediction, not a fabricated one - via "Simulate New CT Study"
(`reveal_next_reserve_study`). "Reset Demo" (`reset_demo_state`) rebuilds
the worklist from that same seed data, so it's always an exact, repeatable
restore.

## Implementation milestones

1. ✅ Scaffolding
2. ✅ Domain model & seed data
3. ✅ Simulated AI Triage Engine
4. ✅ Worklist API + Screen 1
5. ✅ Simulate New Study workflow
6. ✅ Reading Experience — Screen 2
7. ✅ Confirm / Override + feedback capture
8. ⬜ Resilience & clinical polish
9. 🔶 Demo readiness — Reset Demo, Jump to Finding, and the staged
   three-study initial worklist are done; the full 9-step Demonstration
   Script walkthrough and final README pass are not

Full plan, reasoning, and open assumptions:
`C:\Users\Admin\.claude\plans\sorted-percolating-bengio.md`.

---

## Remaining work (paused here — 2026-08-08)

The core product is fully functional today: every **Must**-priority
requirement in the PRD (AI-01–05, WL-01–05, RD-01–05, FB-01–03) is
implemented and has been verified against the actual running app, not just
unit tests. All six studies' real DICOM are converted and calibrated;
106/106 backend tests pass; frontend builds and lints clean.

**Milestone 8 — Resilience & clinical polish** (not started):
- Simulated "AI service unavailable" fallback banner — worklist keeps
  working without AI prioritization, per the UX doc's fail-safe principle.
  Nothing today exercises this path.
- Accessible color/contrast audit (WCAG AA) across both screens.
- Richer PACS-style metadata / explainability copy, building on what's
  already there (accession number, hemorrhage-location caption).
- *Already done ahead of schedule in Milestones 5/6:* row-reorder highlight
  animation, confidence meter, loading/error states.

**Milestone 9 — Demo readiness** (mostly done):
- ✅ Reset Demo (with confirmation), Jump to Finding, and the staged
  three-study initial worklist (the other three real studies are revealed
  via "Simulate New CT Study") — implemented and manually verified against
  the running app.
- ⬜ Full walkthrough of the Design Spec's 9-step Demonstration Script as a
  final QA pass.
- ⬜ Final README pass once Milestone 8 lands too.
