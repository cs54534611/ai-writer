import { useState } from 'react'
import { useAIContinue, useAIExpand, useAIRewrite } from '../hooks/useChapters'

interface AIWritingPanelProps {
  chapter?: any
  projectId?: string
  onInsertText?: (text: string) => void
  onFeedback: () => void
}

export default function AIWritingPanel({ chapter, projectId, onInsertText, onFeedback }: AIWritingPanelProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [loadingLabel, setLoadingLabel] = useState('')
  const [versions, setVersions] = useState<string[]>([])
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const aiContinue = useAIContinue()
  const aiExpand = useAIExpand()
  const aiRewrite = useAIRewrite()

  const api = '/api/v1'

  const handleAPI = async (url: string, body: any, label: string) => {
    if (!chapter?.content) return
    setIsLoading(true)
    setLoadingLabel(label)
    setError(null)
    setVersions([])
    setSelectedVersion(null)
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
      const data = await res.json()
      return data
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
      setLoadingLabel('')
    }
  }

  const handleContinue = async () => {
    if (!chapter || !projectId) return
    try {
      const result = await aiContinue.mutateAsync({
        projectId,
        chapterId: chapter.id,
        context: chapter.content,
        numVersions: 2,
      })
      if (Array.isArray(result) && result.length > 0) {
        const texts = result.map((r: any) => r.text || r.content || JSON.stringify(r))
        setVersions(texts)
      }
    } catch (err) {
      console.error('AI 续写失败:', err)
    }
  }

  const handleExpand = async (ratio: number) => {
    if (!chapter || !projectId) return
    const paragraph = chapter.content
    try {
      const data = await handleAPI(
        `${api}/projects/${projectId}/chapters/${chapter.id}/expand`,
        { paragraph, expand_ratio: ratio },
        `AI 扩写 ${ratio}x...`
      )
      if (data?.expanded) {
        onInsertText?.(data.expanded)
      }
    } catch (err) {
      console.error('AI 扩写失败:', err)
    }
  }

  const handleRewrite = async (mode: string) => {
    if (!chapter || !projectId) return
    try {
      const data = await handleAPI(
        `${api}/projects/${projectId}/chapters/${chapter.id}/rewrite`,
        { content: chapter.content, mode },
        `AI 改写 (${mode})...`
      )
      if (data?.rewritten) {
        onInsertText?.(data.rewritten)
      }
    } catch (err) {
      console.error('AI 改写失败:', err)
    }
  }

  const handleEnhance = async () => {
    if (!chapter || !projectId) return
    try {
      const data = await handleAPI(
        `${api}/projects/${projectId}/chapters/${chapter.id}/enhance`,
        { content: chapter.content, senses: ['视觉', '听觉', '嗅觉', '触觉'] },
        'AI 描写增强...'
      )
      if (data?.enhanced) {
        onInsertText?.(data.enhanced)
      }
    } catch (err) {
      console.error('AI 描写增强失败:', err)
    }
  }

  const handleSelectVersion = (index: number) => {
    setSelectedVersion(index)
  }

  const handleInsertSelected = () => {
    if (selectedVersion !== null && versions[selectedVersion]) {
      onInsertText?.(versions[selectedVersion])
      setVersions([])
      setSelectedVersion(null)
    }
  }

  const rewriteModes = [
    { key: 'polish', label: '润色' },
    { key: 'alternative', label: '替代表达' },
    { key: 'humor', label: '幽默' },
    { key: 'suspense', label: '悬疑' },
  ]

  return (
    <div className="p-4 space-y-4">
      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
          {error}
        </div>
      )}

      {/* 操作按钮 */}
      <div className="space-y-2">
        <button
          onClick={handleContinue}
          disabled={!chapter?.content || isLoading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {isLoading && loadingLabel === 'AI 续写中...' ? loadingLabel : '✨ AI 续写'}
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleExpand(1.5)}
            disabled={!chapter?.content || isLoading}
            className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 disabled:opacity-50 text-sm"
          >
            {isLoading && loadingLabel.includes('1.5') ? '...' : '扩写 1.5x'}
          </button>
          <button
            onClick={() => handleExpand(2)}
            disabled={!chapter?.content || isLoading}
            className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 disabled:opacity-50 text-sm"
          >
            {isLoading && loadingLabel.includes('2x') ? '...' : '扩写 2x'}
          </button>
        </div>

        {/* 改写选项 */}
        <div className="pt-2 border-t">
          <p className="text-xs text-gray-500 mb-2">改写风格</p>
          <div className="grid grid-cols-2 gap-1">
            {rewriteModes.map(item => (
              <button
                key={item.key}
                onClick={() => handleRewrite(item.key)}
                disabled={!chapter?.content || isLoading}
                className="px-2 py-1.5 text-xs bg-gray-50 text-gray-700 rounded hover:bg-gray-100 disabled:opacity-50"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={onFeedback}
          disabled={!chapter?.content || isLoading}
          className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 disabled:opacity-50 text-sm"
        >
          💬 AI 即时反馈
        </button>

        <button
          onClick={handleEnhance}
          disabled={!chapter?.content || isLoading}
          className="w-full px-4 py-2 bg-orange-50 text-orange-700 rounded-lg hover:bg-orange-100 disabled:opacity-50 text-sm"
        >
          {isLoading && loadingLabel.includes('描写增强') ? '...' : '🎨 描写增强'}
        </button>
      </div>

      {/* 多版本候选 */}
      {versions.length > 0 && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-gray-500">续写版本（选择其一）：</p>
            {selectedVersion !== null && (
              <button
                onClick={handleInsertSelected}
                className="text-xs text-blue-600 hover:underline"
              >
                插入选中版本
              </button>
            )}
          </div>
          <div className="space-y-2">
            {versions.map((v, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg text-sm cursor-pointer transition-colors ${
                  selectedVersion === i ? 'bg-blue-50 border-2 border-blue-300' : 'bg-gray-50 hover:bg-gray-100'
                }`}
                onClick={() => handleSelectVersion(i)}
              >
                <p className="text-gray-700 whitespace-pre-wrap">{v}</p>
                {selectedVersion === i && (
                  <button className="mt-2 text-xs text-blue-600 hover:underline">
                    ✓ 已选择 — 点击"插入选中版本"
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
