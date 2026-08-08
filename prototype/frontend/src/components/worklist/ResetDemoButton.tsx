interface ResetDemoButtonProps {
  onClick: () => void
  disabled: boolean
}

// Deliberately styled distinctly from SimulateStudyButton (outlined, not
// filled) - it's a destructive/hard-to-reverse action, so it shouldn't read
// as equally weighted with "add a study". The confirmation step itself
// lives in WorklistPage (see ConfirmDialog).
export function ResetDemoButton({ onClick, disabled }: ResetDemoButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-2 rounded-md border border-clinical-border px-4 py-2 text-sm font-medium text-clinical-text transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-slate-900"
    >
      {disabled ? 'Resetting…' : 'Reset Demo'}
    </button>
  )
}
