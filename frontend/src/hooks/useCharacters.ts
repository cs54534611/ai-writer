import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Character, CreateCharacterInput } from '../types'

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

interface ListResponse {
  items: any[]
  total: number
  page: number
  page_size: number
}

export function useCharacters(projectId: string) {
  return useQuery({
    queryKey: ['characters', projectId],
    queryFn: async () => {
      const data: ListResponse = await fetchJSON(`${API}/projects/${projectId}/characters`)
      return data.items
    },
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

export function useCharacter(projectId: string, id: string) {
  return useQuery({
    queryKey: ['character', projectId, id],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/characters/${id}`),
    enabled: !!projectId && !!id,
  })
}

export function useCreateCharacter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CreateCharacterInput & { project_id: string }) =>
      fetchJSON(`${API}/projects/${data.project_id}/characters`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['characters', data.project_id] }),
    onError: (err) => {
      console.error(`[useCreateCharacter] 创建角色失败:`, err)
    },
  })
}

export function useUpdateCharacter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: Partial<Character> }) =>
      fetchJSON(`${API}/projects/${projectId}/characters/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['characters', data.project_id] }),
    onError: (err, _, context) => {
      console.error(`[useUpdateCharacter] 更新角色失败:`, err)
    },
  })
}

export function useDeleteCharacter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/characters/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['characters', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useDeleteCharacter] 删除角色失败:`, err)
    },
  })
}
