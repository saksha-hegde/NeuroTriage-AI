# data/

`seed_studies.json` — the initial worklist (6 studies, already `Completed` /
`Ready`, one for each row of the prioritization policy table plus a spare ICH
and a spare normal case). `priority` is intentionally **not** stored here —
`StudyRepository` derives it from each study's prediction via
`app.core.prioritization.determine_priority` at load time, so the policy has
exactly one source of truth.

## Adding real CT images (DICOM)

1. For each study you want to populate, create
   `dicom_source/{study_id}/` (matching a `seed_studies.json` id, e.g.
   `dicom_source/STU-001/`) and copy that study's anonymized `.dcm` files
   into it. `dicom_source/` doesn't exist until you create it - it's
   git-ignored, your DICOM never gets committed.
2. From `backend/`, with the venv active, run:
   ```
   python -m scripts.convert_dicom
   ```
3. This writes `images/{study_id}/slice_000.png, slice_001.png, ...` - each
   a **16-bit grayscale PNG holding the raw Hounsfield-unit data**
   (RescaleSlope/RescaleIntercept already applied, but *not* windowed - see
   `app/services/dicom_conversion.py`), plus `images/{study_id}/window_default.json`
   if the source DICOM carried its own WindowCenter/WindowWidth. It also
   **automatically updates `slice_count`** in `seed_studies.json` for every
   study it converted.
4. **Not automatic:** for any `Suspected ICH` study, open the converted
   images (e.g. via the viewer once running, cycling window presets) and
   adjust that study's `prediction.overlay_region` (`x`, `y`, `width`,
   `height`, `slice_index` - all 0-1 fractions except `slice_index`) by hand
   so the highlighted box actually lines up with where the hemorrhage is
   visible. The script only clamps `slice_index` into the new valid range so
   it doesn't point past the end of a real study with fewer slices than the
   placeholder assumed - it can't know where the finding actually is.

Safe to re-run any time (e.g. after fixing a source file) - each study's
`images/{study_id}/` folder is cleared and rewritten from scratch.

## Window/level (windowing)

Conversion no longer bakes in a single window - it preserves the full HU
range, and `GET /studies/{id}/slices/{n}` applies windowing **per request**
against that preserved data (see `app/services/windowing.py`), selected via
a `?preset=` query param:

- `brain` (default) - WW 80 / WL 40, the standard soft-tissue brain window.
- `blood` - WW 100 / WL 50, tuned for hemorrhage conspicuity.
- `dicom` - the source DICOM's own WindowCenter/WindowWidth, if it had one
  (falls back to `brain` otherwise).

Because windowing happens at request time, switching presets in the viewer
never requires re-running `convert_dicom` - only the original DICOM ->
HU-PNG step above does.

The API/frontend never touch DICOM directly - `GET /studies/{id}/slices/{n}`
only ever reads a PNG that's already been converted, windows it, and
returns a fresh 8-bit PNG. A study with no converted images yet (or a slice
index that hasn't been reached) shows an honest "not available yet" state
in the viewer rather than a broken image.
