import { useNavigate } from 'react-router-dom'
import type { Study } from '../../types/study'
import { PriorityBadge } from './PriorityBadge'
import { AIStatusBadge, StudyStatusBadge } from './StatusBadge'

interface WorklistTableProps {
  studies: Study[]
  /** Study ids to briefly highlight (just changed status/priority). */
  updatedIds?: Set<string>
}

// Design Spec Screen 1: Patient Name, Study, Study Status, AI Status, AI Priority.
// WL-05: selecting a study opens the Reading Experience.
export function WorklistTable({ studies, updatedIds }: WorklistTableProps) {
  const navigate = useNavigate()

  const openStudy = (studyId: string) => navigate(`/studies/${studyId}`)

  return (
    <table className="w-full border-collapse text-left text-sm">
      <thead>
        <tr className="border-b border-clinical-border text-xs uppercase tracking-wide text-clinical-muted">
          <th className="px-4 py-3 font-medium">Patient Name</th>
          <th className="px-4 py-3 font-medium">Study</th>
          <th className="px-4 py-3 font-medium">Study Status</th>
          <th className="px-4 py-3 font-medium">AI Status</th>
          <th className="px-4 py-3 font-medium">AI Priority</th>
        </tr>
      </thead>
      <tbody>
        {studies.map((study) => {
          const justUpdated = updatedIds?.has(study.id) ?? false
          return (
            <tr
              key={study.id}
              onClick={() => openStudy(study.id)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') openStudy(study.id)
              }}
              tabIndex={0}
              role="button"
              aria-label={`Open ${study.patient_name}'s study`}
              className={`cursor-pointer border-b border-clinical-border last:border-0 transition-colors duration-1000 hover:bg-slate-50 focus:outline-none focus-visible:bg-slate-100 dark:hover:bg-slate-900/50 dark:focus-visible:bg-slate-900 ${
                justUpdated ? 'bg-amber-50 dark:bg-amber-950/40' : ''
              }`}
            >
              <td className="px-4 py-3 font-medium text-clinical-text">{study.patient_name}</td>
              <td className="px-4 py-3 text-clinical-muted">{study.study_description}</td>
              <td className="px-4 py-3">
                <StudyStatusBadge status={study.study_status} />
              </td>
              <td className="px-4 py-3">
                <AIStatusBadge status={study.ai_status} />
              </td>
              <td className="px-4 py-3">
                <PriorityBadge priority={study.priority} />
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
