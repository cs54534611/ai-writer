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

export interface SensitiveWord {
  id: string
  project_id: string
  word: string
  level: 'hint' | 'warning' | 'danger'
  category: 'politics' | 'adult' | 'violence' | 'custom'
  created_at: string
}

export function useSensitiveWords(projectId: string) {
  return useQuery({
    queryKey: ['sensitive-words', projectId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/sensitive-words`),
    staleTime: 5 * 60 * 1000,
  })
}

export function useCreateSensitiveWord() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, data }: { projectId: string; data: Partial<SensitiveWord> }) =>
      fetchJSON(`${API}/projects/${projectId}/sensitive-words`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['sensitive-words', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useCreateSensitiveWord] 添加敏感词失败:`, err)
    },
  })
}

export function useDeleteSensitiveWord() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/sensitive-words/${id}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['sensitive-words', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useDeleteSensitiveWord] 删除敏感词失败:`, err)
    },
  })
}

export function useCheckSensitiveWords() {
  return useMutation({
    mutationFn: async ({ projectId, content }: { projectId: string; content: string }) =>
      fetchJSON(`${API}/projects/${projectId}/sensitive-words/check`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      }),
    onError: (err, { projectId }) => {
      console.error(`[useCheckSensitiveWords] 敏感词检测失败:`, err)
    },
  })
}
