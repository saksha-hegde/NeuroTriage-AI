import type { Assessment, Study, WindowPreset } from '../types/study'
import type { Feedback, FeedbackDecision } from '../types/feedback'

/**
 * Thin fetch wrapper. Relative paths only - the Vite dev server proxies
 * `/api/*` to the FastAPI backend (see vite.config.ts), so this code never
 * needs to know the backend's host/port.
 */
async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init)
  if (!response.ok) {
    // FastAPI error responses carry a JSON {"detail": "..."} body - surface
    // it when present (e.g. "Study 'X' has already been reported") rather
    // than just the numeric status.
    const detail = await response
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined)
    throw new Error(
      detail ?? `API request failed: ${init?.method ?? 'GET'} ${path} -> ${response.status}`,
    )
  }
  return response.json() as Promise<T>
}

function postJson<T>(path: string, body: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function fetchWorklist(): Promise<Study[]> {
  return apiFetch<Study[]>('/studies')
}

export function fetchStudy(studyId: string): Promise<Study> {
  return apiFetch<Study>(`/studies/${studyId}`)
}

export function simulateNewStudy(): Promise<Study> {
  return apiFetch<Study>('/studies/simulate', { method: 'POST' })
}

/** "Reset Demo": restores the worklist to its initial three-study state and
 * clears simulated studies / Confirm-Override decisions server-side.
 * Returns the fresh worklist so the caller doesn't need a second fetch. */
export function resetDemo(): Promise<Study[]> {
  return apiFetch<Study[]>('/studies/reset', { method: 'POST' })
}

/** Not a fetch - just builds the URL an <img> src consumes directly. Window/
 * level (`preset`) is a query param, not a fetch/re-render concern - the
 * browser just requests a new image when it changes. */
export function sliceImageUrl(
  studyId: string,
  sliceIndex: number,
  preset: WindowPreset = 'brain',
): string {
  return `/api/studies/${studyId}/slices/${sliceIndex}?preset=${preset}`
}

export function submitFeedback(
  studyId: string,
  decision: FeedbackDecision,
  overriddenAssessment?: Assessment,
): Promise<Feedback> {
  return postJson<Feedback>(`/studies/${studyId}/feedback`, {
    decision,
    overridden_assessment: overriddenAssessment ?? null,
  })
}
