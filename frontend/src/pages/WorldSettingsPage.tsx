import { useState, useEffect, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import type { WorldSetting } from '../types'

type SettingCategory = '人物' | '地点' | '物品' | '组织' | '概念'

const CATEGORY_TABS: { key: SettingCategory; label: string; icon: string }[] = [
  { key: '人物', label: '人物', icon: '👤' },
  { key: '地点', label: '地点', icon: '📍' },
  { key: '物品', label: '物品', icon: '🔮' },
  { key: '组织', label: '组织', icon: '🏛️' },
  { key: '概念', label: '概念', icon: '💡' },
]

interface WorldSettingFormData {
  category: SettingCategory
  name: string
  content: string
  related_setting_ids: string[]
}

const emptyForm: WorldSettingFormData = {
  category: '人物',
  name: '',
  content: '',
  related_setting_ids: [],
}

export default function WorldSettingsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [settings, setSettings] = useState<WorldSetting[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState<SettingCategory>('人物')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingSetting, setEditingSetting] = useState<WorldSetting | null>(null)
  const [formData, setFormData] = useState<WorldSettingFormData>(emptyForm)
  const [searchQuery, setSearchQuery] = useState('')

  // 获取设定列表
  useEffect(() => {
    fetchSettings()
  }, [projectId])

  const fetchSettings = async () => {
    if (!projectId) return
    setIsLoading(true)
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/world-settings/`)
      if (!response.ok) throw new Error('获取设定失败')
      const data = await response.json()
      setSettings(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setIsLoading(false)
    }
  }

  // 按类别筛选
  const filteredSettings = useMemo(() => {
    let result = settings.filter(s => s.category === activeCategory)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      result = result.filter(s => 
        s.name.toLowerCase().includes(query) || 
        s.content.toLowerCase().includes(query)
      )
    }
    return result
  }, [settings, activeCategory, searchQuery])

  // 计算每个设定的关联数量
  const getRelatedCount = (setting: WorldSetting) => {
    return setting.related_setting_ids?.length || 0
  }

  // 获取设定摘要
  const getSummary = (content: string, maxLength = 80) => {
    if (content.length <= maxLength) return content
    return content.slice(0, maxLength) + '...'
  }

  // 打开创建弹窗
  const openCreateModal = () => {
    setEditingSetting(null)
    setFormData(emptyForm)
    setShowModal(true)
  }

  // 打开编辑弹窗
  const openEditModal = (setting: WorldSetting) => {
    setEditingSetting(setting)
    setFormData({
      category: setting.category as SettingCategory,
      name: setting.name,
      content: setting.content,
      related_setting_ids: setting.related_setting_ids || [],
    })
    setShowModal(true)
  }

  // 关闭弹窗
  const closeModal = () => {
    setShowModal(false)
    setEditingSetting(null)
    setFormData(emptyForm)
  }

  // 创建/更新设定
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectId || !formData.name.trim()) return

    try {
      const url = editingSetting 
        ? `/api/v1/projects/${projectId}/world-settings/${editingSetting.id}`
        : `/api/v1/projects/${projectId}/world-settings/`
      
      const method = editingSetting ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!response.ok) throw new Error(editingSetting ? '更新失败' : '创建失败')
      
      await fetchSettings()
      closeModal()
    } catch (err) {
      console.error('Failed to save setting:', err)
      alert(err instanceof Error ? err.message : '操作失败')
    }
  }

  // 删除设定
  const handleDelete = async (id: string) => {
    if (!projectId || !confirm('确定要删除这个设定吗？')) return

    try {
      const response = await fetch(`/api/v1/projects/${projectId}/world-settings/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) throw new Error('删除失败')
      
      await fetchSettings()
      setExpandedId(null)
    } catch (err) {
      console.error('Failed to delete setting:', err)
      alert(err instanceof Error ? err.message : '删除失败')
    }
  }

  // 获取关联设定名称
  const getRelatedSettingNames = (ids: string[]) => {
    return ids
      .map(id => settings.find(s => s.id === id)?.name)
      .filter(Boolean)
      .join(', ')
  }

  // 获取类别颜色
  const getCategoryColor = (category: SettingCategory) => {
    const colors: Record<SettingCategory, string> = {
      '人物': 'bg-blue-100 text-blue-700 border-blue-200',
      '地点': 'bg-green-100 text-green-700 border-green-200',
      '物品': 'bg-purple-100 text-purple-700 border-purple-200',
      '组织': 'bg-orange-100 text-orange-700 border-orange-200',
      '概念': 'bg-pink-100 text-pink-700 border-pink-200',
    }
    return colors[category]
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
        <div className="text-red-500">加载失败: {error}</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">世界设定百科</h2>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + 创建设定
        </button>
      </div>

      {/* 类别 Tab 切换 */}
      <div className="flex gap-2 mb-6 border-b border-gray-200 pb-4">
        {CATEGORY_TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveCategory(tab.key)
              setExpandedId(null)
            }}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              activeCategory === tab.key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            <span className={`px-2 py-0.5 text-xs rounded-full ${
              activeCategory === tab.key ? 'bg-indigo-500' : 'bg-gray-200'
            }`}>
              {settings.filter(s => s.category === tab.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* 搜索框 */}
      <div className="mb-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="搜索设定名称或内容..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* 设定列表 */}
      {filteredSettings.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="mb-4">
            {searchQuery ? '没有找到匹配的设定' : `暂无${activeCategory}类设定`}
          </p>
          {!searchQuery && (
            <button onClick={openCreateModal} className="text-indigo-600 hover:underline">
              创建第一个{activeCategory}设定
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSettings.map(setting => (
            <div
              key={setting.id}
              className={`bg-white rounded-lg border transition-all cursor-pointer ${
                expandedId === setting.id 
                  ? 'border-indigo-500 shadow-lg' 
                  : 'border-gray-200 hover:border-indigo-300 hover:shadow-md'
              }`}
              onClick={() => setExpandedId(expandedId === setting.id ? null : setting.id)}
            >
              {/* 卡片头部 */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">{setting.name}</h3>
                    <span className={`inline-block px-2 py-0.5 text-xs rounded border mt-1 ${getCategoryColor(setting.category as SettingCategory)}`}>
                      {setting.category}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {getRelatedCount(setting)} 个关联
                  </span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {getSummary(setting.content)}
                </p>
              </div>

              {/* 展开内容 */}
              {expandedId === setting.id && (
                <div className="border-t border-gray-200 p-4 bg-gray-50 rounded-b-lg">
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">详细内容</h4>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{setting.content}</p>
                  </div>

                  {/* 关联设定 */}
                  {setting.related_setting_ids && setting.related_setting_ids.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">关联设定</h4>
                      <div className="flex flex-wrap gap-1">
                        {setting.related_setting_ids.map(id => {
                          const related = settings.find(s => s.id === id)
                          return related ? (
                            <span
                              key={id}
                              className="px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded"
                            >
                              {related.name}
                            </span>
                          ) : null
                        })}
                      </div>
                    </div>
                  )}

                  {/* 操作按钮 */}
                  <div className="flex justify-end gap-2 mt-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        openEditModal(setting)
                      }}
                      className="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      编辑
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(setting.id)
                      }}
                      className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      删除
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 创建/编辑弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingSetting ? '编辑设定' : '创建设定'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    设定名称 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    类别
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value as SettingCategory })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {CATEGORY_TABS.map(tab => (
                      <option key={tab.key} value={tab.key}>{tab.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    设定内容 *
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    关联设定
                  </label>
                  <select
                    multiple
                    value={formData.related_setting_ids}
                    onChange={(e) => {
                      const selected = Array.from(e.target.selectedOptions).map(opt => opt.value)
                      setFormData({ ...formData, related_setting_ids: selected })
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 h-32"
                  >
                    {settings
                      .filter(s => s.id !== editingSetting?.id)
                      .map(setting => (
                        <option key={setting.id} value={setting.id}>
                          {setting.category} - {setting.name}
                        </option>
                      ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">按住 Ctrl/Cmd 多选</p>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={!formData.name.trim() || !formData.content.trim()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {editingSetting ? '保存' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
