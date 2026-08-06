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
3. This writes `images/{study_id}/slice_000.png, slice_001.png, ...`
   (windowed to 8-bit grayscale - see `app/services/dicom_conversion.py` for
   exactly how) and **automatically updates `slice_count`** in
   `seed_studies.json` for every study it converted.
4. **Not automatic:** for any `Suspected ICH` study, open the converted PNGs
   and adjust that study's `prediction.overlay_region` (`x`, `y`, `width`,
   `height`, `slice_index` - all 0-1 fractions except `slice_index`) by hand
   so the highlighted box actually lines up with where the hemorrhage is
   visible. The script only clamps `slice_index` into the new valid range so
   it doesn't point past the end of a real study with fewer slices than the
   placeholder assumed - it can't know where the finding actually is.

Safe to re-run any time (e.g. after fixing a source file) - each study's
`images/{study_id}/` folder is cleared and rewritten from scratch.

The API/frontend never touch DICOM directly - `GET /studies/{id}/slices/{n}`
only ever serves a PNG that's already been converted. A study with no
converted images yet (or a slice index that hasn't been reached) shows an
honest "not available yet" state in the viewer rather than a broken image.
