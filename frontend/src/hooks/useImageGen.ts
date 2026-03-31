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

export interface ImageGenerateParams {
  prompt: string
  style?: 'anime' | 'realistic' | 'ink' | 'watercolor'
  character_ids?: string[]
}

export interface ProjectImage {
  id: string
  project_id: string
  character_id?: string
  prompt: string
  style: string
  image_url: string
  image_data?: string // base64
  created_at: string
}

export function useProjectImages(projectId: string) {
  return useQuery({
    queryKey: ['project-images', projectId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/images`),
    enabled: !!projectId,
  })
}

export function useCharacterImages(projectId: string, characterId: string) {
  return useQuery({
    queryKey: ['character-images', projectId, characterId],
    queryFn: () => fetchJSON(`${API}/projects/${projectId}/characters/${characterId}/images`),
    enabled: !!projectId && !!characterId,
  })
}

export function useGenerateImage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, params }: { projectId: string; params: ImageGenerateParams }) => {
      const res = await fetchJSON(`${API}/projects/${projectId}/images/generate`, {
        method: 'POST',
        body: JSON.stringify(params),
      })
      return { projectId, data: res }
    },
    onSuccess: ({ projectId }) => {
      qc.invalidateQueries({ queryKey: ['project-images', projectId] })
    },
    onError: (err, { projectId }) => {
      console.error(`[useGenerateImage] 生成图片失败:`, err)
    },
  })
}

export function useGetCharacterImage() {
  return useMutation({
    mutationFn: async ({ projectId, characterId }: { projectId: string; characterId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/characters/${characterId}/image`),
    onError: (err, { projectId, characterId }) => {
      console.error(`[useGetCharacterImage] 获取角色图片失败:`, err)
    },
  })
}

export function useApplyImageToCharacter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, characterId, imageId }: { projectId: string; characterId: string; imageId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/characters/${characterId}/image`, {
        method: 'PUT',
        body: JSON.stringify({ image_id: imageId }),
      }),
    onSuccess: (_, { projectId, characterId }) => {
      qc.invalidateQueries({ queryKey: ['character', projectId, characterId] })
      qc.invalidateQueries({ queryKey: ['characters', projectId] })
    },
    onError: (err, { projectId, characterId }) => {
      console.error(`[useApplyImageToCharacter] 应用角色图片失败:`, err)
    },
  })
}

export function useDeleteImage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, imageId }: { projectId: string; imageId: string }) =>
      fetchJSON(`${API}/projects/${projectId}/images/${imageId}`, { method: 'DELETE' }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: ['project-images', projectId] })
    },
    onError: (err, { projectId }) => {
      console.error(`[useDeleteImage] 删除图片失败:`, err)
    },
  })
}
