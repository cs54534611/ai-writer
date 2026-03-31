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

export interface TimelineEvent {
  id: string
  project_id: string
  title: string
  description: string | null
  time_point: string
  character_ids: string | null
  location_id: string | null
  event_type: string
  sort_order: number
  created_at: string
}

export function useTimelineEvents(projectId: string, eventType?: string) {
  const url = eventType 
    ? `${API}/projects/${projectId}/timeline-events?event_type=${eventType}`
    : `${API}/projects/${projectId}/timeline-events`
  
  return useQuery({
    queryKey: ['timeline-events', projectId, eventType],
    queryFn: () => fetchJSON(url),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000,
  })
}

export function useTimelineEvent(projectId: string, id: string) {
  return useQuery({
    queryKey: ['timeline-event', projectId, id],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/timeline-events/${id}`),
    enabled: !!projectId && !!id,
  })
}

export function useCreateTimelineEvent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<TimelineEvent, 'id' | 'created_at'> & { project_id: string }) =>
      fetchJSON(`${API}/projects/${data.project_id}/timeline-events`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['timeline-events', data.project_id] }),
    onError: (err) => {
      console.error('[useCreateTimelineEvent] 创建时间线事件失败:', err)
    },
  })
}

export function useUpdateTimelineEvent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId, data }: { id: string; projectId: string; data: Partial<TimelineEvent> }) =>
      fetchJSON(`${API}/projects/${projectId}/timeline-events/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) =>
      qc.invalidateQueries({ queryKey: ['timeline-events', data.project_id] }),
    onError: (err) => {
      console.error('[useUpdateTimelineEvent] 更新时间线事件失败:', err)
    },
  })
}

export function useDeleteTimelineEvent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, projectId }: { id: string; projectId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/timeline-events/${id}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) =>
      qc.invalidateQueries({ queryKey: ['timeline-events', projectId] }),
    onError: (err, { projectId }) => {
      console.error('[useDeleteTimelineEvent] 删除时间线事件失败:', err)
    },
  })
}
