import type { Assessment, Prediction } from './study'

/**
 * Mirrors backend/app/models/schemas.py's FeedbackRequest/Feedback.
 * "Reject" exists in the backend's domain enum for forward compatibility
 * but has no UI/API path in the MVP, so it's deliberately not a value here.
 */
export type FeedbackDecision = 'Confirm' | 'Override'

export interface Feedback {
  id: string
  study_id: string
  prediction_snapshot: Prediction
  decision: FeedbackDecision
  overridden_assessment: Assessment | null
  recorded_at: string
}
