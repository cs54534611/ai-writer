import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Inspiration, CreateInspirationInput, InspirationTag } from '../types'

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

export function useInspirations(projectId: string, tag?: InspirationTag) {
  const url = tag
    ? `${API}/projects/${projectId}/inspirations?tag=${encodeURIComponent(tag)}`
    : `${API}/projects/${projectId}/inspirations`
  return useQuery({
    queryKey: ['inspirations', projectId, tag],
    queryFn: async () => {
      const data = await fetchJSON(url)
      return Array.isArray(data) ? data : (data.items ?? [])
    },
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

export function useCreateInspiration() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CreateInspirationInput) =>
      fetchJSON(`${API}/projects/${data.project_id}/inspirations`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['inspirations', data.project_id] }),
    onError: (err) => {
      console.error(`[useCreateInspiration] 创建灵感失败:`, err)
    },
  })
}

export function useUpdateInspiration() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: Partial<Inspiration> }) =>
      fetchJSON(`${API}/projects/${projectId}/inspirations/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['inspirations', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useUpdateInspiration] 更新灵感失败:`, err)
    },
  })
}

export function useDeleteInspiration() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/inspirations/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['inspirations', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useDeleteInspiration] 删除灵感失败:`, err)
    },
  })
}

export function useElevateInspiration() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, to }: { id: string; projectId: string; to: 'character' | 'outline' }) =>
      fetchJSON(`${API}/projects/${projectId}/inspirations/${id}/elevate`, {
        method: 'POST',
        body: JSON.stringify({ to }),
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['inspirations', projectId] })
      qc.invalidateQueries({ queryKey: ['characters', projectId] })
    },
    onError: (err, { projectId }) => {
      console.error(`[useElevateInspiration] 提升灵感失败:`, err)
    },
  })
}
