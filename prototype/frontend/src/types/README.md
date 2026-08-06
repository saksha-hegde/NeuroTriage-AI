# types/

TypeScript interfaces mirroring the backend's Pydantic schemas
(`app/models/schemas.py`) — kept in sync by hand, no shared codegen:

- `study.ts` — `Study`, `Prediction`, `OverlayRegion`, and the
  `StudyStatus` / `AIStatus` / `Assessment` / `Priority` enums.
- `feedback.ts` — `Feedback`, `FeedbackDecision` (`'Confirm' | 'Override'`
  only — `Reject` exists on the backend as a reserved value but isn't
  exposed here since there's no UI path to it).
