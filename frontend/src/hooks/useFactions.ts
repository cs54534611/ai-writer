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

export interface Faction {
  id: string
  project_id: string
  name: string
  parent_id: string | null
  color: string
  description: string | null
  created_at: string
  updated_at: string
}

export function useFactions(projectId: string) {
  return useQuery({
    queryKey: ['factions', projectId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/factions`),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000,
  })
}

export function useFaction(projectId: string, id: string) {
  return useQuery({
    queryKey: ['faction', projectId, id],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/factions/${id}`),
    enabled: !!projectId && !!id,
  })
}

export function useCreateFaction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<Faction, 'id' | 'created_at' | 'updated_at'> & { project_id: string }) =>
      fetchJSON(`${API}/projects/${data.project_id}/factions`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['factions', data.project_id] }),
    onError: (err) => {
      console.error('[useCreateFaction] 创建势力失败:', err)
    },
  })
}

export function useUpdateFaction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: Partial<Faction> }) =>
      fetchJSON(`${API}/projects/${projectId}/factions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['factions', data.project_id] }),
    onError: (err) => {
      console.error('[useUpdateFaction] 更新势力失败:', err)
    },
  })
}

export function useDeleteFaction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/factions/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['factions', projectId] }),
    onError: (err, { projectId }) => {
      console.error('[useDeleteFaction] 删除势力失败:', err)
    },
  })
}
