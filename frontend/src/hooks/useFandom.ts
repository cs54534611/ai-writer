import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const API = '/api/v1'

async function fetchJSON(url: string, opts?: RequestInit) {
  const res = await fetch(url, {
    ...opts,
    headers: { 'Content-Type': 'application/json', ...opts?.headers },
  })
  if (!res.ok) throw new Error(`${url} ${res.status}`)
  if (res.status === 204) return null
  return res.json()
}

export interface FandomSource {
  id: string
  project_id: string
  source_text: string
  extracted_characters: string[]
  extracted_world: string
  extracted_style: string
  created_at: string
}

export interface FandomOutline {
  title: string
  summary: string
  chapters: {
    title: string
    summary: string
    scenes: string[]
  }[]
}

export function useFandomSources(projectId: string) {
  return useQuery({
    queryKey: ['fandom-sources', projectId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/fandom/sources`),
    enabled: !!projectId,
  })
}

export function useFandomSource(projectId: string, sourceId: string) {
  return useQuery({
    queryKey: ['fandom-source', projectId, sourceId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/fandom/sources/${sourceId}`),
    enabled: !!projectId && !!sourceId,
  })
}

export function useImportFandom() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, sourceText }: { projectId: string; sourceText: string }) => {
      const res = await fetchJSON(`${API}/projects/${projectId}/fandom/import`, {
        method: 'POST',
        body: JSON.stringify({ source_text: sourceText }),
      })
      return { projectId, data: res }
    },
    onSuccess: ({ projectId }) => {
      qc.invalidateQueries({ queryKey: ['fandom-sources', projectId] })
    },
  })
}

export function useGenerateFandomOutline() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      sourceId,
      params,
    }: {
      projectId: string
      sourceId: string
      params: {
        selected_characters?: string[]
        tone?: string
        focus_areas?: string[]
      }
    }) => {
      const res = await fetchJSON(`${API}/projects/${projectId}/fandom/sources/${sourceId}/outline`, {
        method: 'POST',
        body: JSON.stringify(params),
      })
      return { projectId, sourceId, data: res }
    },
    onSuccess: ({ projectId, sourceId }) => {
      qc.invalidateQueries({ queryKey: ['fandom-source', projectId, sourceId] })
    },
  })
}

export function useCreateProjectFromFandom() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      sourceId,
      outline,
    }: {
      projectId: string
      sourceId: string
      outline: FandomOutline
    }) => {
      const res = await fetchJSON(`${API}/projects/${projectId}/fandom/sources/${sourceId}/create`, {
        method: 'POST',
        body: JSON.stringify({ outline }),
      })
      return { projectId, data: res }
    },
    onSuccess: ({ projectId }) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })
}

export function useDeleteFandomSource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, sourceId }: { projectId: string; sourceId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/fandom/sources/${sourceId}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['fandom-sources', projectId] })
    },
  })
}
