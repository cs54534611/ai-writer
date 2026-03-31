import { useState, useCallback } from 'react'

const API_BASE = '/api/v1'

export interface Plugin {
  id: string
  name: string
  version: string
  description: string
  author: string
  hooks: string[]
  enabled: boolean
  config: Record<string, any>
  source: 'builtin' | 'thirdparty'
}

export function usePlugins() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const getPlugins = useCallback(async (): Promise<Plugin[]> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins`)
      if (!response.ok) throw new Error('Failed to fetch plugins')
      return await response.json()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const enablePlugin = useCallback(async (pluginId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins/${pluginId}/enable`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to enable plugin')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const disablePlugin = useCallback(async (pluginId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins/${pluginId}/disable`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to disable plugin')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const getPluginConfig = useCallback(async (pluginId: string): Promise<Record<string, any>> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins/${pluginId}/config`)
      if (!response.ok) throw new Error('Failed to get plugin config')
      return await response.json()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const savePluginConfig = useCallback(async (pluginId: string, config: Record<string, any>): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins/${pluginId}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (!response.ok) throw new Error('Failed to save plugin config')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const executePlugin = useCallback(async (pluginId: string, context: Record<string, any>): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/plugins/${pluginId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context),
      })
      if (!response.ok) throw new Error('Failed to execute plugin')
      return await response.json()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    loading,
    error,
    getPlugins,
    enablePlugin,
    disablePlugin,
    getPluginConfig,
    savePluginConfig,
    executePlugin,
  }
}
