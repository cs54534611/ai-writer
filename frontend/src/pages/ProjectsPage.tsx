import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjects, useCreateProject } from '../hooks/useProjects'

export default function ProjectsPage() {
  const { data: projects, isLoading, error } = useProjects()
  const createProject = useCreateProject()
  const navigate = useNavigate()
  const [showModal, setShowModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProjectName.trim()) return
    
    try {
      await createProject.mutateAsync({ name: newProjectName })
      setNewProjectName('')
      setShowModal(false)
    } catch (err) {
      console.error('Failed to create project:', err)
    }
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
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">我的项目</h2>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + 新建项目
        </button>
      </div>

      {projects && projects.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="mb-4">还没有任何项目</p>
          <button
            onClick={() => setShowModal(true)}
            className="text-blue-600 hover:underline"
          >
            创建第一个项目
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects?.map((project) => (
            <div
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
            >
              <h3 className="font-semibold text-gray-900 mb-2">{project.name}</h3>
              {project.description && (
                <p className="text-sm text-gray-500 mb-2 line-clamp-2">{project.description}</p>
              )}
              <p className="text-xs text-gray-400">
                创建于 {new Date(project.created_at).toLocaleDateString('zh-CN')}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">新建项目</h3>
            <form onSubmit={handleCreate}>
              <input
                type="text"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                placeholder="项目名称"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setNewProjectName('')
                  }}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={!newProjectName.trim() || createProject.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createProject.isPending ? '创建中...' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
