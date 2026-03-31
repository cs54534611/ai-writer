import { useState, useEffect, useCallback } from 'react'
import type { Location } from '../types'

const API_BASE = '/api/v1'

export function useLocations(projectId: string) {
  const [data, setData] = useState<Location[] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchLocations = useCallback(async () => {
    if (!projectId) return
    
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/locations`)
      if (!response.ok) throw new Error('Failed to fetch locations')
      const result = await response.json()
      setData(result.data || [])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData([])
    } finally {
      setIsLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    fetchLocations()
  }, [fetchLocations])

  return {
    data,
    isLoading,
    error,
    refetch: fetchLocations,
  }
}
