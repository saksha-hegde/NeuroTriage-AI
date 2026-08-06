import type { Priority } from '../../types/study'

const PRIORITY_STYLES: Record<Priority, string> = {
  Critical: 'bg-priority-critical-bg text-priority-critical',
  High: 'bg-priority-high-bg text-priority-high',
  Moderate: 'bg-priority-moderate-bg text-priority-moderate',
  Routine: 'bg-priority-routine-bg text-priority-routine',
}

// Matches the UX Workflow & Trust Design prioritization policy table
// exactly - same four labels, same emoji, used nowhere else so this stays
// the single place the mapping is defined.
const PRIORITY_ICON: Record<Priority, string> = {
  Critical: '🔴',
  High: '🟠',
  Moderate: '🟡',
  Routine: '🟢',
}

interface PriorityBadgeProps {
  priority: Priority | null
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  if (priority === null) {
    return <span className="text-sm text-clinical-muted">—</span>
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${PRIORITY_STYLES[priority]}`}
    >
      <span aria-hidden="true">{PRIORITY_ICON[priority]}</span>
      {priority}
    </span>
  )
}
