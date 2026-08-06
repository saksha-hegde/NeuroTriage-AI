import { useCallback, useEffect, useState } from 'react'
import { fetchStudy } from './client'
import type { Study } from '../types/study'

interface UseStudyResult {
  study: Study | null
  loading: boolean
  error: string | null
  /** Re-fetch on demand - used after recording feedback (Milestone 7) so
   * the Reading screen reflects the study's new "Reported" status without
   * a full page reload. */
  refetch: () => Promise<void>
}

export function useStudy(studyId: string | undefined): UseStudyResult {
  const [study, setStudy] = useState<Study | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!studyId) return
    setLoading(true)
    try {
      const data = await fetchStudy(studyId)
      setStudy(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load study')
    } finally {
      setLoading(false)
    }
  }, [studyId])

  useEffect(() => {
    load()
  }, [load])

  return { study, loading, error, refetch: load }
}
