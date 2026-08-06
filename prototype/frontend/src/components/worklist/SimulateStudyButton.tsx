interface SimulateStudyButtonProps {
  onClick: () => void
  disabled: boolean
}

export function SimulateStudyButton({ onClick, disabled }: SimulateStudyButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
    >
      {disabled ? 'Simulating…' : 'Simulate New CT Study'}
    </button>
  )
}
