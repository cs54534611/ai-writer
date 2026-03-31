import { useState, useCallback, KeyboardEvent } from 'react'
import { useParams } from 'react-router-dom'
import { useInspirations, useCreateInspiration, useElevateInspiration } from '../hooks/useInspirations'
import type { InspirationTag } from '../types'

const TAG_OPTIONS: { value: InspirationTag; label: string; color: string }[] = [
  { value: 'character', label: '人物', color: 'bg-purple-100 text-purple-700' },
  { value: 'scene', label: '场景', color: 'bg-green-100 text-green-700' },
  { value: 'plot', label: '情节', color: 'bg-blue-100 text-blue-700' },
  { value: 'dialogue', label: '对话', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'setting', label: '设定', color: 'bg-gray-100 text-gray-700' },
]

export default function InspirationsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [selectedTag, setSelectedTag] = useState<InspirationTag | undefined>(undefined)
  const [content, setContent] = useState('')
  const [selectedInspirationTag, setSelectedInspirationTag] = useState<InspirationTag>('plot')

  const { data: inspirations, isLoading, error } = useInspirations(projectId!, selectedTag)
  const createInspiration = useCreateInspiration()
  const elevateInspiration = useElevateInspiration()

  const handleCreate = useCallback(async () => {
    if (!projectId || !content.trim()) return
    
    try {
      await createInspiration.mutateAsync({
        project_id: projectId,
        content: content.trim(),
        tags: [selectedInspirationTag],
      })
      setContent('')
    } catch (err) {
      console.error('Failed to create inspiration:', err)
    }
  }, [projectId, content, selectedInspirationTag, createInspiration])

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      handleCreate()
    }
  }, [handleCreate])

  const handleElevate = async (id: string, to: 'character' | 'outline') => {
    try {
      await elevateInspiration.mutateAsync({ id, projectId, to })
    } catch (err) {
      console.error('Failed to elevate inspiration:', err)
    }
  }

  const getTagStyle = (tag: InspirationTag) => {
    return TAG_OPTIONS.find(t => t.value === tag)?.color || 'bg-gray-100 text-gray-700'
  }

  const getTagLabel = (tag: InspirationTag) => {
    return TAG_OPTIONS.find(t => t.value === tag)?.label || tag
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-red-500">加载失败: {error instanceof Error ? error.message : 'Unknown error'}</div>
      </div>
    )
  }

  return (
    <div className="p-8 flex flex-col h-full">
      {/* Quick Add Section */}
      <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">快速记录灵感</h3>
        <div className="flex gap-2 mb-3">
          {TAG_OPTIONS.map(tag => (
            <button
              key={tag.value}
              onClick={() => setSelectedInspirationTag(tag.value)}
              className={`px-3 py-1 text-sm rounded-full transition-colors ${
                selectedInspirationTag === tag.value
                  ? tag.color
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tag.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="写下你的灵感... (Ctrl+Enter 快速提交)"
            rows={2}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          <button
            onClick={handleCreate}
            disabled={!content.trim() || createInspiration.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 self-end"
          >
            添加
          </button>
        </div>
      </div>

      {/* Filter Tags */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setSelectedTag(undefined)}
          className={`px-3 py-1 text-sm rounded-full transition-colors ${
            selectedTag === undefined
              ? 'bg-gray-800 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          全部
        </button>
        {TAG_OPTIONS.map(tag => (
          <button
            key={tag.value}
            onClick={() => setSelectedTag(tag.value)}
            className={`px-3 py-1 text-sm rounded-full transition-colors ${
              selectedTag === tag.value
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tag.label}
          </button>
        ))}
      </div>

      {/* Inspirations Grid */}
      {inspirations && inspirations.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <p>还没有灵感记录</p>
        </div>
      ) : (
        <div className="flex-1 overflow-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {inspirations?.map((inspiration) => (
              <div
                key={inspiration.id}
                className={`p-4 bg-white rounded-lg border border-gray-200 ${
                  inspiration.is_elevated ? 'opacity-60' : ''
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`px-2 py-0.5 text-xs rounded-full ${getTagStyle(inspiration.tag)}`}>
                    {getTagLabel(inspiration.tag)}
                  </span>
                  {inspiration.is_elevated && (
                    <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700">
                      已升格
                    </span>
                  )}
                </div>
                <p className="text-gray-700 whitespace-pre-wrap mb-3">{inspiration.content}</p>
                {!inspiration.is_elevated && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleElevate(inspiration.id, 'character')}
                      disabled={elevateInspiration.isPending}
                      className="px-2 py-1 text-xs text-purple-600 hover:bg-purple-50 rounded"
                    >
                      → 角色卡
                    </button>
                    <button
                      onClick={() => handleElevate(inspiration.id, 'outline')}
                      disabled={elevateInspiration.isPending}
                      className="px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded"
                    >
                      → 大纲
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
