import { useNavigate } from 'react-router-dom'
import { useOutlines } from '../hooks/useOutlines'

interface OutlineTreeProps {
  projectId: string
  currentChapterId?: string
}

export default function OutlineTree({ projectId, currentChapterId }: OutlineTreeProps) {
  const navigate = useNavigate()
  const { data: outlineNodes } = useOutlines(projectId)

  // 简单树形渲染：卷→章两级
  const renderNode = (node: any, level: number = 0) => {
    const isActive = node.id === currentChapterId || node.chapter_id === currentChapterId
    return (
      <div key={node.id} className="select-none">
        <div
          onClick={() => {
            if (node.chapter_id) {
              navigate(`/projects/${projectId}/writing/chapters/${node.chapter_id}`)
            }
          }}
          className={`py-1.5 px-2 text-sm rounded cursor-pointer flex items-center gap-1 ${
            isActive
              ? 'bg-blue-100 text-blue-700 font-medium'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
        >
          {node.line_type === 'main' ? '📖' : node.line_type === 'branch' ? '🌿' : '🔖'}
          <span className="truncate">{node.title}</span>
          {node.word_target && (
            <span className="ml-auto text-xs text-gray-400">{node.word_target}字</span>
          )}
        </div>
        {/* 子节点 */}
        {node.children?.map((child: any) => renderNode(child, level + 1))}
      </div>
    )
  }

  if (!outlineNodes || outlineNodes.length === 0) {
    return (
      <div className="p-4 text-sm text-gray-400 text-center">
        暂无大纲<br />
        <button
          onClick={() => {/* TODO: 创建大纲 */}}
          className="mt-2 text-blue-600 hover:underline text-xs"
        >
          快速生成大纲
        </button>
      </div>
    )
  }

  return (
    <div className="py-2">
      {outlineNodes.map(node => renderNode(node))}
    </div>
  )
}
