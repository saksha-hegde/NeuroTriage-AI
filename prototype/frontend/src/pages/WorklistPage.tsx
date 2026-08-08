import { useState } from 'react'
import { useWorklist } from '../api/useWorklist'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { ResetDemoButton } from '../components/worklist/ResetDemoButton'
import { SimulateStudyButton } from '../components/worklist/SimulateStudyButton'
import { WorklistTable } from '../components/worklist/WorklistTable'

export function WorklistPage() {
  const {
    studies,
    loading,
    error,
    updatedIds,
    simulateStudy,
    simulating,
    resetDemoState,
    resetting,
  } = useWorklist()
  const [confirmingReset, setConfirmingReset] = useState(false)

  async function handleConfirmReset() {
    await resetDemoState()
    setConfirmingReset(false)
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-clinical-text">CT Brain Worklist</h2>
          <p className="text-sm text-clinical-muted">{studies.length} studies</p>
        </div>
        <div className="flex items-center gap-3">
          <ResetDemoButton onClick={() => setConfirmingReset(true)} disabled={resetting} />
          <SimulateStudyButton onClick={simulateStudy} disabled={simulating} />
        </div>
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

      {confirmingReset && (
        <ConfirmDialog
          title="Reset Demo?"
          message="This clears every simulated study and Confirm/Override decision, and restores the worklist to its starting state (Jordan Ellis, Ahmed Farouk, Maria Castillo). Your real DICOM files and converted images are never touched."
          confirmLabel="Reset Demo"
          onConfirm={handleConfirmReset}
          onCancel={() => setConfirmingReset(false)}
          busy={resetting}
        />
      )}
    </div>
  )
}
