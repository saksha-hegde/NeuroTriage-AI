import type { OverlayRegion } from '../../types/study'

interface JumpToFindingButtonProps {
  overlay: OverlayRegion | null
  onJump: () => void
}

/**
 * Single-click navigation to the AI's highlighted slice
 * (overlay.slice_index - the same metadata CTImageViewer already uses to
 * position the overlay, no separate config). Hidden entirely when there's
 * no overlay to jump to, rather than shown disabled - there's nothing
 * useful to communicate about a control with no destination.
 */
export function JumpToFindingButton({ overlay, onJump }: JumpToFindingButtonProps) {
  if (!overlay) return null

  return (
    <button
      type="button"
      onClick={onJump}
      className="rounded border border-clinical-border px-3 py-1 text-sm text-clinical-text transition-colors hover:bg-slate-50 dark:hover:bg-slate-900"
    >
      Jump to Finding
    </button>
  )
}
