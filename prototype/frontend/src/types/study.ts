/**
 * Mirrors backend/app/models/schemas.py. Keep these two in sync by hand -
 * there's no shared codegen for an MVP this size, so a schema change on
 * either side should be reflected here in the same commit.
 */

export type StudyStatus = 'Acquiring' | 'Completed' | 'Reported'

export type AIStatus = 'Processing' | 'Ready'

export type Assessment = 'Suspected ICH' | 'No Suspicious Findings'

export type Priority = 'Critical' | 'High' | 'Moderate' | 'Routine'

/**
 * CT viewer window/level preset - mirrors the `preset` query param on
 * GET /studies/{id}/slices/{n} (see backend/app/services/windowing.py).
 * "dicom" means "the source DICOM's own WindowCenter/WindowWidth", falling
 * back server-side to "brain" if the study's DICOM didn't carry one.
 */
export type WindowPreset = 'brain' | 'blood' | 'dicom'

export interface OverlayRegion {
  slice_index: number
  x: number
  y: number
  width: number
  height: number
}

export interface Prediction {
  assessment: Assessment
  confidence: number
  hemorrhage_location: string | null
  overlay_region: OverlayRegion | null
  predicted_at: string
}

export interface Study {
  id: string
  patient_name: string
  accession_number: string
  study_description: string
  exam_datetime: string
  study_status: StudyStatus
  ai_status: AIStatus | null
  priority: Priority | null
  prediction: Prediction | null
  slice_count: number
}
