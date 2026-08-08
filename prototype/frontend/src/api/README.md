# api/

- `client.ts` — thin fetch wrapper (`/api` proxied to the backend by Vite),
  plus one function per endpoint: `fetchWorklist`, `fetchStudy`,
  `simulateNewStudy`, `resetDemo`, `sliceImageUrl`, `submitFeedback`.
- `useWorklist.ts` — polls the worklist every 2s and tracks which studies
  just changed (for the row highlight). Also exposes `resetDemoState` -
  applies the server's fresh three-study response and re-seeds the
  highlight-tracking snapshot from it, since a reset is a full state
  replacement, not a change worth flashing.
- `useStudy.ts` — loads one study for the Reading Experience, with a
  `refetch` for after feedback is submitted.
