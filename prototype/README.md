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
> Study workflow; Reading Experience; Confirm/Override + feedback capture).
> See [Implementation milestones](#implementation-milestones) below, and
> [Adding your real CT images](#adding-your-real-ct-images) to finish wiring
> up your DICOM files.

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

Open http://localhost:5173 for the worklist. Click a row to open the Reading
Experience for that study, or "Simulate New CT Study" to watch a study move
through Acquiring → Processing → Ready and reprioritize live. API docs are
auto-generated at http://localhost:8000/docs.

## Testing

```bash
cd backend
pytest
```

---

## Adding your real CT images

The Reading Experience is built and works today — without images, it shows
an honest "CT image not available yet" state instead of a broken viewer, so
everything else (slice slider, AI panel, overlay toggle, priority) is fully
demoable already. To wire in your real anonymized DICOM:

```bash
cd backend
mkdir -p app/data/dicom_source/STU-001   # one folder per study you're populating
# copy that study's anonymized .dcm files into it, then repeat for
# STU-002 .. STU-006 (or whichever studies you want to populate)

python -m scripts.convert_dicom
```

This converts each study's slices to PNGs in `app/data/images/{study_id}/`
and automatically updates `slice_count` in `seed_studies.json`. It also
prints a reminder: for any Suspected ICH study, review the converted images
and adjust `overlay_region` (x/y/width/height/slice_index) by hand in
`seed_studies.json` so the highlighted region actually lines up with what's
visible — that's not something conversion can infer. Full details:
`backend/app/data/README.md`.

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
  DICOM is converted to plain PNGs ahead of time (`scripts/convert_dicom.py`)
  so the viewer and API only ever deal with static images, never DICOM
  directly.

Data (v1): seeded from JSON, held in in-memory repository classes
(`backend/app/repositories/`). No database yet — repositories are the seam
where SQLite would be introduced later without touching routes or the
frontend.

## Implementation milestones

1. ✅ Scaffolding
2. ✅ Domain model & seed data
3. ✅ Simulated AI Triage Engine
4. ✅ Worklist API + Screen 1
5. ✅ Simulate New Study workflow
6. ✅ Reading Experience — Screen 2 (pending your real images — see above)
7. ✅ Confirm / Override + feedback capture
8. ⬜ Resilience & clinical polish
9. ⬜ Demo readiness (walk the Design Spec's 9-step demonstration script)

Full plan, reasoning, and open assumptions:
`C:\Users\Admin\.claude\plans\sorted-percolating-bengio.md`.

---

## Remaining work (paused here — 2026-08-07)

The core product is fully functional today: every **Must**-priority
requirement in the PRD (AI-01–05, WL-01–05, RD-01–05, FB-01–03) is
implemented and has been verified against the actual running app, not just
unit tests. 76/76 backend tests pass; frontend builds and lints clean.

**Milestone 8 — Resilience & clinical polish** (not started):
- Simulated "AI service unavailable" fallback banner — worklist keeps
  working without AI prioritization, per the UX doc's fail-safe principle.
  Nothing today exercises this path.
- Accessible color/contrast audit (WCAG AA) across both screens.
- Richer PACS-style metadata / explainability copy, building on what's
  already there (accession number, hemorrhage-location caption).
- *Already done ahead of schedule in Milestones 5/6:* row-reorder highlight
  animation, confidence meter, loading/error states.

**Milestone 9 — Demo readiness** (not started):
- Full walkthrough of the Design Spec's 9-step Demonstration Script as a
  final QA pass — best done once real images are in place.
- A "Reset Demo" action to reseed state without restarting both servers.
- Final README pass.

**Your action item, whenever ready:** drop anonymized `.dcm` files into
`backend/app/data/dicom_source/{study_id}/` and run
`python -m scripts.convert_dicom` (see [above](#adding-your-real-ct-images)).
Not required to keep working — every screen already handles missing images
gracefully — but the sooner it's done, the more the polish/demo passes can
be checked against the real thing.
