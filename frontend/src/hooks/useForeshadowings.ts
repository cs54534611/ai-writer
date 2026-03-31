import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

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

export interface Foreshadowing {
  id: string
  project_id: string
  chapter_id: string
  description: string
  status: 'planted' | 'resolved' | 'expired'
  notes: string | null
  planted_at: string
  resolved_at: string | null
  created_at: string
  updated_at: string
}

export interface ForeshadowingStats {
  total: number
  planted: number
  resolved: number
  expired: number
  resolution_rate: number
}

// 获取伏笔列表
export function useForeshadowings(projectId: string, page = 1, pageSize = 50) {
  return useQuery({
    queryKey: ['foreshadowings', projectId, page, pageSize],
    queryFn: () =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings?page=${page}&page_size=${pageSize}`),
    enabled: !!projectId,
  })
}

// 获取伏笔统计
export function useForeshadowingStats(projectId: string) {
  return useQuery({
    queryKey: ['foreshadowings', 'stats', projectId],
    queryFn: () =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings/stats/summary`),
    enabled: !!projectId,
  })
}

// 创建伏笔
export function useCreateForeshadowing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      chapterId,
      description,
      notes,
    }: {
      projectId: string
      chapterId: string
      description: string
      notes?: string
    }) =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings`, {
        method: 'POST',
        body: JSON.stringify({ chapter_id: chapterId, description, notes }),
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['foreshadowings', projectId] })
      qc.invalidateQueries({ queryKey: ['foreshadowings', 'stats', projectId] })
    },
  })
}

// 更新伏笔
export function useUpdateForeshadowing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      foreshadowingId,
      description,
      status,
      notes,
    }: {
      projectId: string
      foreshadowingId: string
      description?: string
      status?: string
      notes?: string
    }) =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings/${foreshadowingId}`, {
        method: 'PUT',
        body: JSON.stringify({ description, status, notes }),
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['foreshadowings', projectId] })
      qc.invalidateQueries({ queryKey: ['foreshadowings', 'stats', projectId] })
    },
  })
}

// 删除伏笔
export function useDeleteForeshadowing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      foreshadowingId,
    }: {
      projectId: string
      foreshadowingId: string
    }) =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings/${foreshadowingId}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['foreshadowings', projectId] })
      qc.invalidateQueries({ queryKey: ['foreshadowings', 'stats', projectId] })
    },
  })
}

// 回收伏笔
export function useResolveForeshadowing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      foreshadowingId,
    }: {
      projectId: string
      foreshadowingId: string
    }) =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings/${foreshadowingId}/resolve`, {
        method: 'POST',
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['foreshadowings', projectId] })
      qc.invalidateQueries({ queryKey: ['foreshadowings', 'stats', projectId] })
    },
  })
}

// 标记伏笔失效
export function useExpireForeshadowing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      projectId,
      foreshadowingId,
    }: {
      projectId: string
      foreshadowingId: string
    }) =>
      fetchJSON(`${API}/projects/${projectId}/foreshadowings/${foreshadowingId}/expire`, {
        method: 'POST',
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['foreshadowings', projectId] })
      qc.invalidateQueries({ queryKey: ['foreshadowings', 'stats', projectId] })
    },
  })
}
