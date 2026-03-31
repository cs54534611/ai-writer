import { useState, useCallback } from 'react'

const API_BASE = '/api/v1'

export type ExportFormat = 'json' | 'markdown' | 'zip' | 'txt'
export type ChapterExportFormat = 'markdown' | 'txt' | 'json'
export type WorldSettingsExportFormat = 'md' | 'json'

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

export function useChapterExport() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exportChapterMarkdown = useCallback(async (chapterId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/chapters/${chapterId}/export-markdown`)
      if (!response.ok) throw new Error('Failed to export chapter')
      const result = await response.json()
      if (result.data?.content) {
        downloadTextFile(result.data.content, `chapter-${chapterId}.md`)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const exportChapterText = useCallback(async (chapterId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/chapters/${chapterId}/export-text`)
      if (!response.ok) throw new Error('Failed to export chapter')
      const result = await response.json()
      if (result.data?.content) {
        downloadTextFile(result.data.content, `chapter-${chapterId}.txt`)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const exportChapterJSON = useCallback(async (chapterId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/chapters/${chapterId}/export-json`)
      if (!response.ok) throw new Error('Failed to export chapter')
      const result = await response.json()
      if (result.data) {
        downloadTextFile(JSON.stringify(result.data, null, 2), `chapter-${chapterId}.json`)
      }
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
    exportChapterMarkdown,
    exportChapterText,
    exportChapterJSON,
  }
}

export function useWorldSettingsExport() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exportWorldSettings = useCallback(async (
    projectId: string, 
    format: WorldSettingsExportFormat = 'md'
  ): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `${API_BASE}/projects/${projectId}/world-settings/export?format=${format}`
      )
      if (!response.ok) throw new Error('Failed to export world settings')
      const result = await response.json()
      
      if (result.success) {
        if (format === 'json') {
          downloadTextFile(
            JSON.stringify(result.data, null, 2), 
            `world-settings-${projectId}.json`
          )
        } else {
          downloadTextFile(
            result.data.content, 
            `world-settings-${projectId}.md`
          )
        }
      } else {
        throw new Error(result.error || 'Export failed')
      }
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
    exportWorldSettings,
  }
}

function downloadTextFile(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export function useExportPDF() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exportProjectPDF = useCallback(async (projectId: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/export-pdf`)
      if (!response.ok) throw new Error('Failed to export PDF')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${projectId}_export.pdf`
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

  return {
    loading,
    error,
    exportProjectPDF,
  }
}
