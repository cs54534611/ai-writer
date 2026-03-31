import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useProject } from '../hooks/useProjects'
import CharactersPage from './CharactersPage'
import RelationshipGraph from './RelationshipGraph'
import InspirationsPage from './InspirationsPage'

type TabType = 'characters' | 'relationships' | 'inspirations' | 'outline' | 'content'

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { data: project, isLoading, error } = useProject(projectId!)
  const [activeTab, setActiveTab] = useState<TabType>('characters')

  const tabs: { key: TabType; label: string }[] = [
    { key: 'characters', label: '角色' },
    { key: 'relationships', label: '关系图谱' },
    { key: 'inspirations', label: '灵感' },
    { key: 'outline', label: '大纲' },
    { key: 'content', label: '正文' },
  ]

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
    <div className="flex flex-col h-full">
      {/* Project Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => navigate('/projects')}
            className="text-gray-500 hover:text-gray-700"
          >
            ← 返回
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{project?.name}</h1>
        </div>

        {project?.description && (
          <p className="text-gray-600 mb-4">{project.description}</p>
        )}

        <div className="flex gap-6 text-sm text-gray-500">
          <span>创建于 {project?.created_at ? new Date(project.created_at).toLocaleDateString('zh-CN') : '-'}</span>
          <span>|</span>
          <span>字数统计 (TODO)</span>
          <span>|</span>
          <span>章节数 (TODO)</span>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 mt-4 -mb-4">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key)
                navigate(`/projects/${projectId}/${tab.key}`)
              }}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.key
                  ? 'bg-white text-blue-600 border-t-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden bg-gray-50">
        {activeTab === 'characters' && <CharactersPage />}
        {activeTab === 'relationships' && <RelationshipGraph />}
        {activeTab === 'inspirations' && <InspirationsPage />}
        {activeTab === 'outline' && (
          <div className="flex items-center justify-center h-full text-gray-500">
            大纲编辑 (TODO)
          </div>
        )}
        {activeTab === 'content' && (
          <div className="flex items-center justify-center h-full text-gray-500">
            正文编辑 (TODO)
          </div>
        )}
      </div>
    </div>
  )
}
