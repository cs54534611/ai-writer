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

export function useOutlines(projectId: string) {
  return useQuery({
    queryKey: ['outlines', projectId],
    queryFn: async () => {
      const data = await fetchJSON(`${API}/projects/${projectId}/outlines`)
      return Array.isArray(data) ? data : (data.items ?? [])
    },
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

export function useCreateOutline() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, data }: { projectId: string; data: any }) =>
      fetchJSON(`${API}/projects/${projectId}/outlines`, { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['outlines', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useCreateOutline] 创建大纲失败:`, err)
    },
  })
}

export function useUpdateOutline() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: any }) =>
      fetchJSON(`${API}/projects/${projectId}/outlines/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['outlines', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useUpdateOutline] 更新大纲失败:`, err)
    },
  })
}

export function useDeleteOutline() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/outlines/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['outlines', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useDeleteOutline] 删除大纲失败:`, err)
    },
  })
}
