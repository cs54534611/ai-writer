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

export interface ReviewIssue {
  type: 'contradiction' | 'ooc' | 'sensitive'
  severity: 'low' | 'medium' | 'high'
  location: string
  description: string
  suggestion: string
}

export interface ReviewResult {
  score: number
  issues: ReviewIssue[]
  stats: {
    word_count: number
    chapter_count: number
    contradiction_count: number
    ooc_count: number
    sensitive_count: number
  }
}

// 审查单个章节
export function useReviewChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, chapterId, content }: { projectId: string; chapterId: string; content: string }) =>
      fetchJSON(`/api/v1/reviews/chapter`, {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, chapter_id: chapterId, content }),
      }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['chapters', projectId] })
    },
  })
}

// 检查敏感词
export function useCheckSensitive() {
  return useMutation({
    mutationFn: async ({ projectId, content, customWords }: { projectId: string; content: string; customWords?: string[] }) =>
      fetchJSON(`/api/v1/reviews/sensitive`, {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, content, custom_words: customWords }),
      }),
  })
}

// 检查角色 OOC（Out of Character）
export function useCheckOOC() {
  return useMutation({
    mutationFn: async ({ projectId, content, characterId }: { projectId: string; content: string; characterId: string }) =>
      fetchJSON(`/api/v1/reviews/ooc`, {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, content, character_id: characterId }),
      }),
  })
}

// 完整审查（获取完整报告）
export function useCheckFullReview() {
  return useQuery({
    queryKey: ['review', 'full'],
    queryFn: async ({ queryKey }: { queryKey: [string, string, string] }) => {
      const [, projectId, chapterId] = queryKey
      return fetchJSON(`/api/v1/reviews/full`, {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, chapter_id: chapterId }),
      }) as Promise<ReviewResult>
    },
    enabled: false,
  })
}

// 异步触发完整审查（不阻塞）
export function useTriggerFullReview() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, chapterId }: { projectId: string; chapterId: string }) => {
      const res = await fetch(`${API}/projects/${projectId}/chapters/${chapterId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!res.ok) throw new Error(`${res.status}`)
      return res.json()
    },
    onSuccess: (_, { projectId, chapterId }) => {
      qc.invalidateQueries({ queryKey: ['chapters', projectId, chapterId] })
      qc.invalidateQueries({ queryKey: ['review', projectId, chapterId] })
    },
  })
}

// 获取章节审查结果
export function useChapterReview(projectId: string, chapterId: string) {
  return useQuery({
    queryKey: ['review', projectId, chapterId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}/review`),
    enabled: !!chapterId && chapterId !== 'new',
    refetchInterval: 5000, // 每5秒轮询
  })
}

// 应用修复建议
export function useApplyFix() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, chapterId, issueIndex, fixedContent }: { projectId: string; chapterId: string; issueIndex: number; fixedContent: string }) =>
      fetchJSON(`${API}/projects/${projectId}/chapters/${chapterId}/fix`, {
        method: 'POST',
        body: JSON.stringify({ issue_index: issueIndex, fixed_content: fixedContent }),
      }),
    onSuccess: (_, { projectId, chapterId }) => {
      qc.invalidateQueries({ queryKey: ['chapters', projectId, chapterId] })
      qc.invalidateQueries({ queryKey: ['review', projectId, chapterId] })
    },
  })
}
