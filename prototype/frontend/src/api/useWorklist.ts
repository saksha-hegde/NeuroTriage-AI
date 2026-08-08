import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchWorklist, resetDemo, simulateNewStudy } from './client'
import type { Study } from '../types/study'

const POLL_INTERVAL_MS = 2000
// How long a changed row stays highlighted before fading back to normal.
const HIGHLIGHT_DURATION_MS = 2000

interface UseWorklistResult {
  studies: Study[]
  loading: boolean
  error: string | null
  /** Study ids whose status/priority changed on the most recent poll -
   * used to briefly highlight the row so reprioritization is visible
   * without requiring a manual refresh. */
  updatedIds: Set<string>
  simulateStudy: () => Promise<void>
  simulating: boolean
  /** "Reset Demo": restores the initial three-study state server-side and
   * clears local highlight-tracking so nothing flashes as "changed"
   * afterward - a reset is a full state replacement, not an update. */
  resetDemoState: () => Promise<void>
  resetting: boolean
}

function snapshotKey(study: Study): string {
  return `${study.study_status}|${study.ai_status}|${study.priority}`
}

/**
 * Polls the worklist so status/priority changes from the simulated
 * background workflow (AI-05, WL-03) appear without a manual refresh, and
 * tracks which studies just changed so the UI can draw attention to them.
 */
export function useWorklist(): UseWorklistResult {
  const [studies, setStudies] = useState<Study[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updatedIds, setUpdatedIds] = useState<Set<string>>(new Set())
  const [simulating, setSimulating] = useState(false)
  const [resetting, setResetting] = useState(false)

  // Refs, not state - these track bookkeeping that shouldn't itself trigger
  // re-renders (the snapshot map) or needs cleanup across renders (timers).
  const previousSnapshot = useRef<Map<string, string>>(new Map())
  const highlightTimeouts = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())

  const applyStudies = useCallback((data: Study[]) => {
    const changed: string[] = []
    for (const study of data) {
      const prevKey = previousSnapshot.current.get(study.id)
      const nextKey = snapshotKey(study)
      // undefined prevKey = first time we've seen this id (initial load or
      // a brand-new simulated study) - not a "change" worth flashing.
      if (prevKey !== undefined && prevKey !== nextKey) {
        changed.push(study.id)
      }
      previousSnapshot.current.set(study.id, nextKey)
    }

    setStudies(data)
    if (changed.length === 0) return

    setUpdatedIds((prev) => new Set([...prev, ...changed]))
    for (const id of changed) {
      const existing = highlightTimeouts.current.get(id)
      if (existing) clearTimeout(existing)
      highlightTimeouts.current.set(
        id,
        setTimeout(() => {
          setUpdatedIds((prev) => {
            const next = new Set(prev)
            next.delete(id)
            return next
          })
          highlightTimeouts.current.delete(id)
        }, HIGHLIGHT_DURATION_MS),
      )
    }
  }, [])

  const load = useCallback(async () => {
    try {
      const data = await fetchWorklist()
      applyStudies(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load worklist')
    } finally {
      setLoading(false)
    }
  }, [applyStudies])

  useEffect(() => {
    load()
    const interval = setInterval(load, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [load])

  // Clear any pending highlight timers on unmount.
  useEffect(() => {
    const timeouts = highlightTimeouts.current
    return () => {
      timeouts.forEach(clearTimeout)
    }
  }, [])

  const simulateStudy = useCallback(async () => {
    setSimulating(true)
    try {
      await simulateNewStudy()
      await load() // pick up the new "Acquiring" study immediately
    } finally {
      setSimulating(false)
    }
  }, [load])

  const resetDemoState = useCallback(async () => {
    setResetting(true)
    try {
      const fresh = await resetDemo()
      // A reset is a full state replacement, not a series of changes - seed
      // the snapshot map from the fresh data (rather than clearing it) so
      // the *next* poll doesn't misread "wasn't tracked before" as a change
      // and flash every row, and clear any in-flight highlights from
      // before the reset.
      previousSnapshot.current = new Map(fresh.map((study) => [study.id, snapshotKey(study)]))
      highlightTimeouts.current.forEach(clearTimeout)
      highlightTimeouts.current.clear()
      setUpdatedIds(new Set())
      setStudies(fresh)
      setError(null)
    } finally {
      setResetting(false)
    }
  }, [])

  return {
    studies,
    loading,
    error,
    updatedIds,
    simulateStudy,
    simulating,
    resetDemoState,
    resetting,
  }
}
