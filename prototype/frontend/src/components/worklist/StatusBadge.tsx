import type { AIStatus, StudyStatus } from '../../types/study'

const STUDY_STATUS_STYLES: Record<StudyStatus, string> = {
  Acquiring: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
  Completed: 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300',
  Reported: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
}

export function StudyStatusBadge({ status }: { status: StudyStatus }) {
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${STUDY_STATUS_STYLES[status]}`}
    >
      {status}
    </span>
  )
}

/**
 * AI Status is absent until a study reaches StudyStatus "Completed" - there
 * is nothing for the AI Triage Engine to have processed before then (AI-05:
 * worklist priority updates only after AI processing is complete).
 */
export function AIStatusBadge({ status }: { status: AIStatus | null }) {
  if (status === null) {
    return <span className="text-sm text-clinical-muted">—</span>
  }

  if (status === 'Processing') {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-clinical-muted">
        <span
          className="h-2 w-2 animate-pulse rounded-full bg-amber-500"
          aria-hidden="true"
        />
        Processing
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-clinical-text">
      <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden="true" />
      Ready
    </span>
  )
}
