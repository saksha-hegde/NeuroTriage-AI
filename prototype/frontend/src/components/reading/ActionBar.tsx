import type { Assessment } from '../../types/study'

interface ActionBarProps {
  assessment: Assessment
  onConfirm: () => void
  onOverride: (overriddenAssessment: Assessment) => void
  disabled: boolean
}

// Only two possible assessments in this MVP, so "Override" unambiguously
// means "the other one" - no picker needed, and the button label shows
// exactly what will be recorded.
const OTHER_ASSESSMENT: Record<Assessment, Assessment> = {
  'Suspected ICH': 'No Suspicious Findings',
  'No Suspicious Findings': 'Suspected ICH',
}

// RD-05: confirm or override the AI recommendation. Reject is out of MVP
// scope (see FeedbackDecision in the backend schema) - only these two.
export function ActionBar({ assessment, onConfirm, onOverride, disabled }: ActionBarProps) {
  const alternative = OTHER_ASSESSMENT[assessment]

  return (
    <div className="flex gap-3">
      <button
        type="button"
        onClick={onConfirm}
        disabled={disabled}
        className="flex-1 rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
      >
        Confirm
      </button>
      <button
        type="button"
        onClick={() => onOverride(alternative)}
        disabled={disabled}
        className="flex-1 rounded-md border border-clinical-border px-4 py-2 text-sm font-semibold text-clinical-text transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-slate-900"
      >
        Override → {alternative}
      </button>
    </div>
  )
}
