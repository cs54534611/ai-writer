import { useMutation } from '@tanstack/react-query'

const API = '/api/v1'

export interface SearchResult {
  type: 'chapter' | 'character' | 'world_setting'
  id: string
  title: string
  snippet: string
  score: number
}

export function useProjectSearch() {
  return useMutation({
    mutationFn: async ({
      projectId,
      query,
      scope = 'all',
    }: {
      projectId: string
      query: string
      scope?: 'all' | 'chapters' | 'characters' | 'world_settings'
    }) => {
      const url = `${API}/projects/${projectId}/search?q=${encodeURIComponent(query)}&scope=${scope}`
      const res = await fetch(url)
      if (!res.ok) throw new Error(`${url} ${res.status}`)
      return res.json() as Promise<SearchResult[]>
    },
    onError: (err) => {
      console.error(`[useProjectSearch] 全文检索失败:`, err)
    },
  })
}
