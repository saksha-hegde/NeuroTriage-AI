import { useWorklist } from '../api/useWorklist'
import { SimulateStudyButton } from '../components/worklist/SimulateStudyButton'
import { WorklistTable } from '../components/worklist/WorklistTable'

export function WorklistPage() {
  const { studies, loading, error, updatedIds, simulateStudy, simulating } = useWorklist()

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-clinical-text">CT Brain Worklist</h2>
          <p className="text-sm text-clinical-muted">{studies.length} studies</p>
        </div>
        <SimulateStudyButton onClick={simulateStudy} disabled={simulating} />
      </div>

      <div className="overflow-hidden rounded-lg border border-clinical-border bg-clinical-surface">
        {loading && (
          <p className="px-4 py-8 text-center text-sm text-clinical-muted">Loading worklist…</p>
        )}
        {error && (
          <p className="px-4 py-8 text-center text-sm text-priority-critical">
            Couldn't load the worklist: {error}
          </p>
        )}
        {!loading && !error && <WorklistTable studies={studies} updatedIds={updatedIds} />}
      </div>
    </div>
  )
}
