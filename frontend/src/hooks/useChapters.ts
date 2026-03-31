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

export function useChapters(projectId: string) {
  return useQuery({
    queryKey: ['chapters', projectId],
    queryFn: async () => {
      const data = await fetchJSON(`${API}/projects/${projectId}/chapters`)
      return Array.isArray(data) ? data : (data.items ?? [])
    },
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

export function useChapter(projectId: string, chapterId: string) {
  return useQuery({
    queryKey: ['chapters', projectId, chapterId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}`),
    enabled: !!chapterId && chapterId !== 'new',
  })
}

export function useCreateChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, data }: { projectId: string; data: any }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters`, { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['chapters', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useCreateChapter] 创建章节失败:`, err)
    },
  })
}

export function useUpdateChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: any }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['chapters', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useUpdateChapter] 更新章节失败:`, err)
    },
  })
}

export function useDeleteChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) => qc.invalidateQueries({ queryKey: ['chapters', projectId] }),
    onError: (err, { projectId }) => {
      console.error(`[useDeleteChapter] 删除章节失败:`, err)
    },
  })
}

export function useAIContinue() {
  return useMutation({
    mutationFn: async ({ projectId, chapterId, context, numVersions }: { projectId: string; chapterId: string; context: string; numVersions?: number }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}/write`, {
        method: 'POST',
        body: JSON.stringify({ context, num_versions: numVersions }),
      }),
    onError: (err, { projectId }) => {
      console.error(`[useAIContinue] AI 续写失败:`, err)
    },
  })
}

export function useAIExpand() {
  return useMutation({
    mutationFn: async ({ projectId, chapterId, paragraph, ratio }: { projectId: string; chapterId: string; paragraph: string; ratio?: number }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}/expand`, {
        method: 'POST',
        body: JSON.stringify({ paragraph, expand_ratio: ratio }),
      }),
    onError: (err, { projectId }) => {
      console.error(`[useAIExpand] AI 扩写失败:`, err)
    },
  })
}

export function useAIRewrite() {
  return useMutation({
    mutationFn: async ({ projectId, chapterId, content, mode }: { projectId: string; chapterId: string; content: string; mode: string }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}/rewrite`, {
        method: 'POST',
        body: JSON.stringify({ content, mode }),
      }),
    onError: (err, { projectId }) => {
      console.error(`[useAIRewrite] AI 改写失败:`, err)
    },
  })
}

export function useAIFeedback() {
  return useMutation({
    mutationFn: async ({ projectId, content }: { projectId: string; content: string }) =>
      fetchJSON(`${API}/projects/${projectId}/writing/feedback`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      }),
    onError: (err, { projectId }) => {
      console.error(`[useAIFeedback] AI 反馈失败:`, err)
    },
  })
}
