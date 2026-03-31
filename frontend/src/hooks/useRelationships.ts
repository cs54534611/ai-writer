import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Relationship, CreateRelationshipInput, GraphData } from '../types'

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

export function useRelationships(projectId: string) {
  return useQuery({
    queryKey: ['relationships', projectId],
    queryFn: async () => {
      const data = await fetchJSON(`${API}/projects/${projectId}/relationships`)
      return Array.isArray(data) ? data : (data.items ?? [])
    },
    enabled: !!projectId,
  })
}

export function useRelationshipGraph(projectId: string) {
  return useQuery({
    queryKey: ['relationshipGraph', projectId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/relationships/graph`),
    enabled: !!projectId,
  })
}

export function useCreateRelationship() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CreateRelationshipInput) =>
      fetchJSON(`${API}/projects/${data.project_id}/relationships`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['relationships', data.project_id] }),
  })
}

export function useDeleteRelationship() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/relationships/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['relationships', projectId] }),
  })
}
