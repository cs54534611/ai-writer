import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTimelineEvents, useCreateTimelineEvent, useUpdateTimelineEvent, useDeleteTimelineEvent, type TimelineEvent } from '../hooks/useTimelineEvents'

const EVENT_TYPES = ['全部', '主线', '支线', '暗线']
const EVENT_COLORS: Record<string, string> = {
  '主线': 'border-l-4 border-blue-500 bg-blue-50',
  '支线': 'border-l-4 border-green-500 bg-green-50',
  '暗线': 'border-l-4 border-purple-500 bg-purple-50',
}

interface TimelineFormData {
  title: string
  description: string
  time_point: string
  event_type: string
  sort_order: number
}

const emptyForm: TimelineFormData = {
  title: '',
  description: '',
  time_point: '',
  event_type: '主线',
  sort_order: 0,
}

export default function TimelinePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [filterType, setFilterType] = useState('全部')
  const [showModal, setShowModal] = useState(false)
  const [editingEvent, setEditingEvent] = useState<TimelineEvent | null>(null)
  const [formData, setFormData] = useState<TimelineFormData>(emptyForm)

  const { data: events, isLoading, error } = useTimelineEvents(
    projectId!,
    filterType === '全部' ? undefined : filterType
  )
  const createEvent = useCreateTimelineEvent()
  const updateEvent = useUpdateTimelineEvent()
  const deleteEvent = useDeleteTimelineEvent()

  // 按时间点排序
  const sortedEvents = [...(events || [])].sort((a, b) => {
    if (a.time_point !== b.time_point) {
      return a.time_point.localeCompare(b.time_point, undefined, { numeric: true })
    }
    return a.sort_order - b.sort_order
  })

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectId || !formData.title.trim()) return
    
    try {
      await createEvent.mutateAsync({
        project_id: projectId,
        ...formData,
      } as any)
      closeModal()
    } catch (err) {
      console.error('Failed to create event:', err)
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingEvent || !formData.title.trim()) return
    
    try {
      await updateEvent.mutateAsync({
        id: editingEvent.id,
        projectId: projectId!,
        data: formData,
      })
      closeModal()
    } catch (err) {
      console.error('Failed to update event:', err)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个事件吗？')) return
    try {
      await deleteEvent.mutateAsync({ id, projectId: projectId! })
    } catch (err) {
      console.error('Failed to delete event:', err)
    }
  }

  const openCreateModal = () => {
    setEditingEvent(null)
    setFormData(emptyForm)
    setShowModal(true)
  }

  const openEditModal = (event: TimelineEvent) => {
    setEditingEvent(event)
    setFormData({
      title: event.title,
      description: event.description || '',
      time_point: event.time_point,
      event_type: event.event_type,
      sort_order: event.sort_order,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingEvent(null)
    setFormData(emptyForm)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">时间线</h1>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          + 添加事件
        </button>
      </div>

      {/* 过滤标签 */}
      <div className="flex gap-2 mb-6">
        {EVENT_TYPES.map(type => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              filterType === type
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* 时间线视图 */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">加载失败</div>
      ) : sortedEvents.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无事件，点击上方按钮添加第一个事件
        </div>
      ) : (
        <div className="relative">
          {/* 时间线中轴 */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />
          
          {/* 事件列表 */}
          <div className="space-y-4">
            {sortedEvents.map(event => (
              <div
                key={event.id}
                className={`relative ml-16 p-4 rounded-lg ${EVENT_COLORS[event.event_type] || 'border-l-4 border-gray-400 bg-gray-50'}`}
              >
                {/* 时间线节点 */}
                <div className="absolute -left-20 top-4 w-10 h-10 rounded-full bg-white border-4 border-indigo-600 flex items-center justify-center">
                  <div className="w-3 h-3 rounded-full bg-indigo-600" />
                </div>
                
                {/* 时间点 */}
                <div className="text-sm text-gray-500 mb-1">{event.time_point}</div>
                
                {/* 标题 */}
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{event.title}</h3>
                
                {/* 描述 */}
                {event.description && (
                  <p className="text-gray-600 text-sm mb-2">{event.description}</p>
                )}
                
                {/* 标签 */}
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    event.event_type === '主线' ? 'bg-blue-100 text-blue-700' :
                    event.event_type === '支线' ? 'bg-green-100 text-green-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {event.event_type}
                  </span>
                </div>
                
                {/* 操作按钮 */}
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => openEditModal(event)}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(event.id)}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 创建/编辑模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4">
              {editingEvent ? '编辑事件' : '添加事件'}
            </h2>
            <form onSubmit={editingEvent ? handleUpdate : handleCreate}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    事件标题 *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    时间点 *
                  </label>
                  <input
                    type="text"
                    value={formData.time_point}
                    onChange={e => setFormData({ ...formData, time_point: e.target.value })}
                    placeholder="如：第1年3月"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    事件类型
                  </label>
                  <select
                    value={formData.event_type}
                    onChange={e => setFormData({ ...formData, event_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="主线">主线</option>
                    <option value="支线">支线</option>
                    <option value="暗线">暗线</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    排序顺序
                  </label>
                  <input
                    type="number"
                    value={formData.sort_order}
                    onChange={e => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    事件描述
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  {editingEvent ? '保存' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
