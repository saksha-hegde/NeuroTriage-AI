import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { submitFeedback } from '../api/client'
import { useStudy } from '../api/useStudy'
import { AIAssessmentPanel } from '../components/reading/AIAssessmentPanel'
import { ActionBar } from '../components/reading/ActionBar'
import { CTImageViewer } from '../components/reading/CTImageViewer'
import { OverlayToggle } from '../components/reading/OverlayToggle'
import type { Assessment } from '../types/study'

// How long "Feedback Recorded" stays visible before returning to the
// worklist - Design Spec section 5: "briefly displays 'Feedback Recorded',
// and returns to the worklist."
const FEEDBACK_RECORDED_DISPLAY_MS = 1200

// Design Spec Screen 2: CT viewer (left) + AI Assessment panel (right),
// Confirm/Override actions (bottom).
export function ReadingPage() {
  const { studyId } = useParams<{ studyId: string }>()
  const navigate = useNavigate()
  const { study, loading, error } = useStudy(studyId)
  const [sliceIndex, setSliceIndex] = useState(0)
  const [showOverlay, setShowOverlay] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [justRecorded, setJustRecorded] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  if (loading) {
    return <p className="px-6 py-8 text-center text-sm text-clinical-muted">Loading study…</p>
  }

  if (error || !study) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-8">
        <Link to="/" className="text-sm text-clinical-muted hover:underline">
          ← Back to worklist
        </Link>
        <p className="mt-4 text-sm text-priority-critical">
          Couldn't load this study{error ? `: ${error}` : '.'}
        </p>
      </div>
    )
  }

  const overlay = study.prediction?.overlay_region ?? null
  const alreadyReported = study.study_status === 'Reported'

  async function handleDecision(decision: 'Confirm' | 'Override', overriddenAssessment?: Assessment) {
    if (!study) return
    setSubmitting(true)
    setSubmitError(null)
    try {
      await submitFeedback(study.id, decision, overriddenAssessment)
      setJustRecorded(true)
      setTimeout(() => navigate('/'), FEEDBACK_RECORDED_DISPLAY_MS)
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to record feedback')
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <Link to="/" className="text-sm text-clinical-muted hover:underline">
        ← Back to worklist
      </Link>

      <div className="mt-3 mb-6">
        <h2 className="text-base font-semibold text-clinical-text">{study.patient_name}</h2>
        <p className="text-sm text-clinical-muted">
          {study.study_description} · {study.accession_number}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
        <div>
          <CTImageViewer
            studyId={study.id}
            sliceCount={study.slice_count}
            currentIndex={sliceIndex}
            onIndexChange={setSliceIndex}
            overlay={overlay}
            showOverlay={showOverlay}
          />
          <div className="mt-3">
            <OverlayToggle checked={showOverlay} onChange={setShowOverlay} disabled={!overlay} />
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <AIAssessmentPanel prediction={study.prediction} priority={study.priority} />

          {justRecorded && (
            <div className="rounded-md bg-emerald-50 px-4 py-3 text-center text-sm font-medium text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
              Feedback Recorded
            </div>
          )}

          {!justRecorded && alreadyReported && (
            <div className="rounded-md border border-clinical-border bg-clinical-surface px-4 py-3 text-center text-sm text-clinical-muted">
              This study has already been reported.
            </div>
          )}

          {!justRecorded && !alreadyReported && study.prediction && (
            <>
              <ActionBar
                assessment={study.prediction.assessment}
                onConfirm={() => handleDecision('Confirm')}
                onOverride={(overriddenAssessment) =>
                  handleDecision('Override', overriddenAssessment)
                }
                disabled={submitting}
              />
              {submitError && (
                <p className="text-sm text-priority-critical">{submitError}</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
