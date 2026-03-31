import { useState, useCallback } from 'react'

const API_BASE = '/api/v1'

export type ExportFormat = 'json' | 'markdown' | 'zip'

export interface ExportPreview {
  formats: {
    format: ExportFormat
    size: number
    contains: string[]
  }[]
}

export function useExportImport() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exportProject = useCallback(async (projectId: string, format: ExportFormat): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/export?format=${format}`)
      if (!response.ok) throw new Error('Failed to export project')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `project-${projectId}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const importProject = useCallback(async (projectId: string, file: File, format: ExportFormat): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('format', format)

      const response = await fetch(`${API_BASE}/projects/${projectId}/import`, {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) throw new Error('Failed to import project')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const importChaptersFromFolder = useCallback(async (projectId: string, folderPath: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/chapters/import-folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folderPath }),
      })
      if (!response.ok) throw new Error('Failed to import chapters from folder')
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
    exportProject,
    importProject,
    importChaptersFromFolder,
  }
}
