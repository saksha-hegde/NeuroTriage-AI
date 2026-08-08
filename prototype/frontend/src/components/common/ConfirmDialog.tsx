interface ConfirmDialogProps {
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
  busy?: boolean
}

/**
 * A small centered modal for confirming a destructive/hard-to-reverse
 * action (currently just "Reset Demo"). Deliberately plain - no animation
 * library, no portal - this is an MVP prototype, not a design system.
 */
export function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  busy = false,
}: ConfirmDialogProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      role="presentation"
      onClick={onCancel}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-message"
        onClick={(event) => event.stopPropagation()}
        className="w-full max-w-sm rounded-lg border border-clinical-border bg-clinical-surface p-5 shadow-lg"
      >
        <h3 id="confirm-dialog-title" className="text-base font-semibold text-clinical-text">
          {title}
        </h3>
        <p id="confirm-dialog-message" className="mt-2 text-sm text-clinical-muted">
          {message}
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={busy}
            className="rounded-md border border-clinical-border px-4 py-2 text-sm font-medium text-clinical-text transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-slate-900"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={busy}
            className="rounded-md bg-priority-critical px-4 py-2 text-sm font-semibold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? 'Working…' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
