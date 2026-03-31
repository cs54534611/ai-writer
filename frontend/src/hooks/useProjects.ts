import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Project } from '../types'

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

interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  page_size: number
}

async function fetchProjects(): Promise<Project[]> {
  const data: ProjectListResponse = await fetchJSON(`${API}/projects`)
  return data.items
}

async function fetchProject(projectId: string): Promise<Project> {
  return fetchJSON(`${API}/projects/${projectId}`)
}

async function createProject(data: { name: string; genre?: string; description?: string; total_words_target?: number }): Promise<Project> {
  return fetchJSON(`${API}/projects`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

async function updateProject(id: string, data: Partial<Project>): Promise<Project> {
  return fetchJSON(`${API}/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects,
  })
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => fetchProject(projectId),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

export function useCreateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createProject,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
    onError: (err) => {
      console.error('[useCreateProject] 创建项目失败:', err)
    },
  })
}

export function useUpdateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
      updateProject(id, data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['projects', data.id] })
    },
    onError: (err) => {
      console.error('[useUpdateProject] 更新项目失败:', err)
    },
  })
}
