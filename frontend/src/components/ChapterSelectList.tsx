import { useState } from 'react'
import { useChapters } from '../hooks/useChapters'

interface ChapterSelectListProps {
  projectId: string
  selectedChapterIds: string[]
  onSelectionChange: (ids: string[]) => void
  onChapterClick: (chapterId: string) => void
}

export default function ChapterSelectList({
  projectId,
  selectedChapterIds,
  onSelectionChange,
  onChapterClick,
}: ChapterSelectListProps) {
  const { data: chapters, isLoading } = useChapters(projectId)
  const [selectMode, setSelectMode] = useState<'single' | 'batch'>('single')

  const toggleSelection = (id: string) => {
    if (selectMode === 'single') {
      onSelectionChange([id])
    } else {
      if (selectedChapterIds.includes(id)) {
        onSelectionChange(selectedChapterIds.filter((i) => i !== id))
      } else {
        onSelectionChange([...selectedChapterIds, id])
      }
    }
  }

  const selectAll = () => {
    if (chapters) {
      onSelectionChange(chapters.map((c: any) => c.id))
    }
  }

  const clearSelection = () => {
    onSelectionChange([])
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'reviewed':
        return <span className="px-1.5 py-0.5 text-xs rounded bg-green-100 text-green-700">已审查</span>
      case 'completed':
        return <span className="px-1.5 py-0.5 text-xs rounded bg-blue-100 text-blue-700">已完成</span>
      case 'writing':
        return <span className="px-1.5 py-0.5 text-xs rounded bg-yellow-100 text-yellow-700">写作中</span>
      default:
        return <span className="px-1.5 py-0.5 text-xs rounded bg-gray-100 text-gray-600">草稿</span>
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400">
        加载中...
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 头部工具栏 */}
      <div className="p-3 border-b bg-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">选择章节</span>
          <span className="text-xs text-gray-400">({chapters?.length || 0})</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setSelectMode(selectMode === 'single' ? 'batch' : 'single')}
            className={`text-xs px-2 py-1 rounded ${
              selectMode === 'batch' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
            }`}
            title={selectMode === 'single' ? '切换到批量选择' : '切换到单选'}
          >
            {selectMode === 'single' ? '☰ 批量' : '◎ 单选'}
          </button>
        </div>
      </div>

      {/* 批量选择工具栏 */}
      {selectMode === 'batch' && (
        <div className="px-3 py-2 border-b bg-gray-50 flex items-center gap-2">
          <button
            onClick={selectAll}
            className="text-xs text-blue-600 hover:text-blue-700"
          >
            全选
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={clearSelection}
            className="text-xs text-gray-500 hover:text-gray-600"
          >
            清空
          </button>
          {selectedChapterIds.length > 0 && (
            <>
              <span className="text-gray-300">|</span>
              <span className="text-xs text-gray-500">
                已选 {selectedChapterIds.length} 章
              </span>
            </>
          )}
        </div>
      )}

      {/* 章节列表 */}
      <div className="flex-1 overflow-y-auto">
        {chapters && chapters.length > 0 ? (
          <ul className="divide-y">
            {chapters.map((chapter: any) => {
              const isSelected = selectedChapterIds.includes(chapter.id)
              const isReviewed = chapter.status === 'reviewed'

              return (
                <li
                  key={chapter.id}
                  className={`flex items-center gap-3 p-3 cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-blue-50 border-l-2 border-blue-500'
                      : 'hover:bg-gray-50 border-l-2 border-transparent'
                  } ${isReviewed ? 'border-l-4 border-green-400' : ''}`}
                  onClick={() => {
                    if (selectMode === 'single') {
                      onChapterClick(chapter.id)
                    } else {
                      toggleSelection(chapter.id)
                    }
                  }}
                  onDoubleClick={() => onChapterClick(chapter.id)}
                >
                  {/* 选择框（批量模式） */}
                  {selectMode === 'batch' && (
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelection(chapter.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  )}

                  {/* 章节序号 */}
                  <span className="w-6 text-xs text-gray-400 text-center flex-shrink-0">
                    {chapter.sort_order}
                  </span>

                  {/* 章节信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-gray-800 truncate">
                        {chapter.title || `第${chapter.sort_order}章`}
                      </span>
                      {isReviewed && (
                        <span className="text-green-500" title="已审查">✓</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-400">
                        {chapter.word_count?.toLocaleString() || 0} 字
                      </span>
                      {getStatusBadge(chapter.status)}
                    </div>
                  </div>

                  {/* 右箭头 */}
                  <span className="text-gray-300 text-sm">›</span>
                </li>
              )
            })}
          </ul>
        ) : (
          <div className="flex flex-col items-center justify-center h-32 text-gray-400">
            <p className="text-sm">暂无章节</p>
            <p className="text-xs mt-1">请先创建章节</p>
          </div>
        )}
      </div>

      {/* 底部统计 */}
      <div className="p-3 border-t bg-white">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>总字数：{chapters?.reduce((sum: number, c: any) => sum + (c.word_count || 0), 0).toLocaleString() || 0}</span>
          <span>已审查：{chapters?.filter((c: any) => c.status === 'reviewed').length || 0}</span>
        </div>
      </div>
    </div>
  )
}
