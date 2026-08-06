import type { Prediction, Priority } from '../../types/study'
import { PriorityBadge } from '../worklist/PriorityBadge'

interface AIAssessmentPanelProps {
  prediction: Prediction | null
  priority: Priority | null
}

// RD-02/RD-03/RD-04: prediction, confidence, and explainability support,
// presented together per the UX doc ("confidence is always displayed
// together with the prediction").
export function AIAssessmentPanel({ prediction, priority }: AIAssessmentPanelProps) {
  if (!prediction) {
    return (
      <div className="rounded-lg border border-clinical-border bg-clinical-surface p-4 text-sm text-clinical-muted">
        AI assessment not available yet — this study hasn't finished processing.
      </div>
    )
  }

  const confidencePercent = Math.round(prediction.confidence * 100)
  const isSuspectedICH = prediction.assessment === 'Suspected ICH'
  const emphasisClass = isSuspectedICH ? 'text-priority-critical' : 'text-priority-routine'

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-clinical-border bg-clinical-surface p-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-clinical-muted">
          AI Assessment
        </p>
        <p className={`mt-1 text-lg font-semibold ${emphasisClass}`}>{prediction.assessment}</p>
      </div>

      <div>
        <div className="flex items-center justify-between text-xs text-clinical-muted">
          <span>Confidence</span>
          <span className="font-medium text-clinical-text">{confidencePercent}%</span>
        </div>
        <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
          <div
            className={`h-full rounded-full ${isSuspectedICH ? 'bg-priority-critical' : 'bg-priority-routine'}`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-clinical-muted">
          Priority
        </span>
        <PriorityBadge priority={priority} />
      </div>

      {isSuspectedICH && prediction.hemorrhage_location && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-clinical-muted">
            Hemorrhage Location
          </p>
          <p className="mt-1 text-sm text-clinical-text">{prediction.hemorrhage_location}</p>
          {prediction.overlay_region && (
            <p className="mt-1 text-xs text-clinical-muted">
              Highlighted on slice {prediction.overlay_region.slice_index + 1} — toggle "AI
              Overlay" below the viewer to show it.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
