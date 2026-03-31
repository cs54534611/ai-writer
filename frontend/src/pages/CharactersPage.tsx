import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useCharacters, useCreateCharacter, useUpdateCharacter, useDeleteCharacter } from '../hooks/useCharacters'
import type { Character, CreateCharacterInput } from '../types'

const GENDER_OPTIONS = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' },
]

interface CharacterFormData {
  name: string
  gender?: string
  age?: string
  personality?: string
  background?: string
  arc?: string
}

const emptyForm: CharacterFormData = {
  name: '',
  gender: undefined,
  age: undefined,
  personality: '',
  background: '',
  arc: '',
}

export default function CharactersPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: characters, isLoading, error } = useCharacters(projectId!)
  const createCharacter = useCreateCharacter()
  const updateCharacter = useUpdateCharacter()
  const deleteCharacter = useDeleteCharacter()

  const [showModal, setShowModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [formData, setFormData] = useState<CharacterFormData>(emptyForm)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectId || !formData.name.trim()) return
    
    try {
      await createCharacter.mutateAsync({
        name: formData.name,
        gender: formData.gender,
        age: formData.age,
        personality: formData.personality,
        background: formData.background,
        arc: formData.arc,
      } as any)
      closeModal()
    } catch (err) {
      console.error('Failed to create character:', err)
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingCharacter || !formData.name.trim()) return
    
    try {
      await updateCharacter.mutateAsync({
        id: editingCharacter.id,
        projectId: projectId!,
        data: {
          name: formData.name,
          gender: formData.gender,
          age: formData.age,
          personality: formData.personality,
          background: formData.background,
          arc: formData.arc,
        },
      })
      closeModal()
    } catch (err) {
      console.error('Failed to update character:', err)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个角色吗？')) return
    try {
      await deleteCharacter.mutateAsync({ id, projectId: projectId! })
      setShowDetailModal(false)
    } catch (err) {
      console.error('Failed to delete character:', err)
    }
  }

  const openCreateModal = () => {
    setEditingCharacter(null)
    setFormData(emptyForm)
    setShowModal(true)
  }

  const openEditModal = (character: Character) => {
    setEditingCharacter(character)
    setFormData({
      name: character.name,
      gender: character.gender,
      age: character.age,
      personality: character.personality || '',
      background: character.background || '',
      arc: character.arc || '',
    })
    setShowModal(true)
  }

  const openDetailModal = (character: Character) => {
    setSelectedCharacter(character)
    setShowDetailModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setShowDetailModal(false)
    setSelectedCharacter(null)
    setEditingCharacter(null)
    setFormData(emptyForm)
  }

  const getGenderLabel = (gender?: string) => {
    return GENDER_OPTIONS.find(g => g.value === gender)?.label || '未设置'
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
        <h2 className="text-2xl font-bold text-gray-900">角色管理</h2>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + 创建角色
        </button>
      </div>

      {characters && characters.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="mb-4">还没有任何角色</p>
          <button onClick={openCreateModal} className="text-blue-600 hover:underline">
            创建第一个角色
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {characters?.map((character) => (
            <div
              key={character.id}
              onClick={() => openDetailModal(character)}
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
            >
              <div className="flex items-start gap-3">
                {/* 头像区域 */}
                <div className="flex-shrink-0">
                  {character.avatar_url ? (
                    <img
                      src={character.avatar_url}
                      alt={character.name}
                      className="w-14 h-14 rounded-full object-cover border-2 border-gray-200"
                    />
                  ) : (
                    <div 
                      className="w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold"
                      style={{ 
                        backgroundColor: character.gender === 'male' ? '#3b82f6' : 
                                        character.gender === 'female' ? '#ec4899' : '#8b5cf6'
                      }}
                    >
                      {character.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{character.name}</h3>
                      <p className="text-sm text-gray-500">
                        {getGenderLabel(character.gender)} {character.age ? `· ${character.age}岁` : ''}
                      </p>
                    </div>
                    <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                      {character.personality?.slice(0, 4) || '待补充'}
                    </span>
                  </div>
                  {character.background && (
                    <p className="mt-2 text-sm text-gray-600 line-clamp-2">{character.background}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingCharacter ? '编辑角色' : '创建角色'}
            </h3>
            <form onSubmit={editingCharacter ? handleUpdate : handleCreate}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">性别</label>
                    <select
                      value={formData.gender || ''}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value as Character['gender'] || undefined })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">请选择</option>
                      {GENDER_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">年龄</label>
                    <input
                      type="text"
                      value={formData.age || ''}
                      onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">性格特点</label>
                  <input
                    type="text"
                    value={formData.personality || ''}
                    onChange={(e) => setFormData({ ...formData, personality: e.target.value })}
                    placeholder="如：内向、善良、偏执"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">背景故事</label>
                  <textarea
                    value={formData.background || ''}
                    onChange={(e) => setFormData({ ...formData, background: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">角色弧光</label>
                  <textarea
                    value={formData.arc || ''}
                    onChange={(e) => setFormData({ ...formData, arc: e.target.value })}
                    rows={3}
                    placeholder="角色的成长与变化"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  />
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
                  disabled={!formData.name.trim() || createCharacter.isPending || updateCharacter.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createCharacter.isPending || updateCharacter.isPending ? '保存中...' : '保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedCharacter && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{selectedCharacter.name}</h3>
                <p className="text-sm text-gray-500">
                  {getGenderLabel(selectedCharacter.gender)} {selectedCharacter.age ? `· ${selectedCharacter.age}岁` : ''}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setShowDetailModal(false)
                    openEditModal(selectedCharacter)
                  }}
                  className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  编辑
                </button>
                <button
                  onClick={() => handleDelete(selectedCharacter.id)}
                  className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                >
                  删除
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {selectedCharacter.personality && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">性格特点</h4>
                  <p className="text-gray-600">{selectedCharacter.personality}</p>
                </div>
              )}
              {selectedCharacter.background && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">背景故事</h4>
                  <p className="text-gray-600 whitespace-pre-wrap">{selectedCharacter.background}</p>
                </div>
              )}
              {selectedCharacter.arc && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">角色弧光</h4>
                  <p className="text-gray-600 whitespace-pre-wrap">{selectedCharacter.arc}</p>
                </div>
              )}
              {!selectedCharacter.personality && !selectedCharacter.background && !selectedCharacter.arc && (
                <p className="text-gray-400 text-center py-4">暂无详细信息</p>
              )}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={closeModal}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
