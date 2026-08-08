# components/reading/

`CTImageViewer` (slice slider + AI overlay, graceful "not available yet"
fallback when a slice hasn't been converted), `AIAssessmentPanel`
(prediction, confidence meter, priority, hemorrhage location),
`OverlayToggle`, `WindowPresetControl` (Brain / Blood-ICH / DICOM-default
window/level, see the backend's `app/services/windowing.py`),
`JumpToFindingButton` (single-click to `overlay.slice_index` with the
overlay auto-enabled - reuses the same overlay metadata `CTImageViewer`
already positions the highlight from, no separate config; hidden when
there's no overlay to jump to), `ActionBar` (Confirm / Override — Reject is
out of MVP scope, see the backend's `FeedbackDecision` enum).
