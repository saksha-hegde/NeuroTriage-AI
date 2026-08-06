# api/

- `client.ts` — thin fetch wrapper (`/api` proxied to the backend by Vite),
  plus one function per endpoint: `fetchWorklist`, `fetchStudy`,
  `simulateNewStudy`, `sliceImageUrl`, `submitFeedback`.
- `useWorklist.ts` — polls the worklist every 2s and tracks which studies
  just changed (for the row highlight).
- `useStudy.ts` — loads one study for the Reading Experience, with a
  `refetch` for after feedback is submitted.
