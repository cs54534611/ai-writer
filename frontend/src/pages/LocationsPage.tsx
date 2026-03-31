import { useState, useMemo, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useLocations } from '../hooks/useLocations'
import type { Location } from '../types'
import Rough from 'roughjs'

interface LocationWithChildren extends Location {
  children: LocationWithChildren[]
}

const LAYER_NAMES: Record<string, string> = {
  'celestial': '天界/神界',
  'material': '人界/物质界',
  'underworld': '冥界/地狱',
  'realm': '秘境/异空间',
  'void': '虚空',
}

const TERRAIN_ICONS: Record<string, string> = {
  'plains': '🌿',
  'mountain': '⛰️',
  'forest': '🌲',
  'desert': '🏜️',
  'ocean': '🌊',
  'river': '💧',
  'city': '🏙️',
  'village': '🏘️',
  'ruins': '🏛️',
  'swamp': '🌫️',
  'snow': '❄️',
  'volcano': '🌋',
  'cave': '🕳️',
  'sky': '☁️',
  'abyss': '🌀',
}

// 层级颜色配置
const LAYER_COLORS: Record<string, { stroke: string; fill: string; bg: string }> = {
  'celestial': { stroke: '#3b82f6', fill: '#93c5fd', bg: 'rgba(59, 130, 246, 0.1)' },
  'material': { stroke: '#22c55e', fill: '#86efac', bg: 'rgba(34, 197, 94, 0.1)' },
  'underworld': { stroke: '#6b7280', fill: '#9ca3af', bg: 'rgba(107, 114, 128, 0.1)' },
  'realm': { stroke: '#a855f7', fill: '#d8b4fe', bg: 'rgba(168, 85, 247, 0.1)' },
  'void': { stroke: '#1f2937', fill: '#4b5563', bg: 'rgba(31, 41, 55, 0.1)' },
}

// 手绘风格地图组件
function RoughMap({ locations }: { locations: Location[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current || !locations || locations.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rc = Rough.canvas(canvas)

    // 设置画布大小
    const width = canvas.width
    const height = canvas.height

    // 清除画布
    ctx.clearRect(0, 0, width, height)

    // 收集所有连接关系（基于parent_id）
    const connections: { from: Location; to: Location }[] = []
    locations.forEach(loc => {
      if (loc.parent_id) {
        const parent = locations.find(l => l.id === loc.parent_id)
        if (parent) {
          connections.push({ from: parent, to: loc })
        }
      }
    })

    // 计算位置映射（将坐标转换为画布坐标）
    const layerOrder = ['celestial', 'material', 'underworld', 'realm', 'void']

    // 归一化坐标
    const layerLocs: Record<string, Location[]> = {}
    locations.forEach(loc => {
      const layer = loc.layer || 'material'
      if (!layerLocs[layer]) layerLocs[layer] = []
      layerLocs[layer].push(loc)
    })

    // 计算每个layer的位置范围
    const layerY: Record<string, number> = {}
    let currentY = 60
    layerOrder.forEach(layer => {
      layerY[layer] = currentY
      currentY += 120
    })

    // 为每个layer内的位置计算x坐标
    const locPositions: Record<string, { x: number; y: number }> = {}
    Object.entries(layerLocs).forEach(([layer, locs]) => {
      const layerYPos = layerY[layer] || 120
      locs.forEach((loc, idx) => {
        const xOffset = 100 + (idx % 4) * 150
        const yOffset = layerYPos + Math.floor(idx / 4) * 80 + 40
        locPositions[loc.id] = { x: xOffset, y: yOffset }
      })
    })

    // 绘制连接线
    connections.forEach(({ from, to }) => {
      const fromPos = locPositions[from.id]
      const toPos = locPositions[to.id]
      if (fromPos && toPos) {
        rc.line(fromPos.x, fromPos.y, toPos.x, toPos.y, {
          stroke: '#9ca3af',
          strokeWidth: 1.5,
          bowing: 1,
        })
      }
    })

    // 绘制每个地点
    locations.forEach(loc => {
      const pos = locPositions[loc.id]
      if (!pos) return

      const colors = LAYER_COLORS[loc.layer] || LAYER_COLORS['material']
      const radius = 25

      // 绘制手绘风格圆
      rc.circle(pos.x, pos.y, radius * 2, {
        stroke: colors.stroke,
        fill: colors.fill,
        fillStyle: 'solid',
        strokeWidth: 2,
      })

      // 绘制地点名称
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillStyle = '#374151'
      ctx.fillText(loc.name.slice(0, 6), pos.x, pos.y + 4)
    })

  }, [locations])

  return (
    <div className="mt-6 bg-gray-50 rounded-lg p-4 border">
      <h3 className="text-sm font-medium text-gray-600 mb-3">📍 世界地图概览</h3>
      <canvas
        ref={canvasRef}
        width={650}
        height={500}
        className="w-full bg-white/50 rounded border"
      />
      <div className="flex gap-4 mt-3 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-blue-400"></span> 天界
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-green-400"></span> 人界
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-gray-400"></span> 冥界
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-purple-400"></span> 秘境
        </span>
      </div>
    </div>
  )
}

interface LocationFormData {
  name: string
  description: string
  layer: string
  parent_id: string | null
  position_x: number
  position_y: number
  position_z: number
  terrain: string | null
}

const emptyForm: LocationFormData = {
  name: '',
  description: '',
  layer: 'material',
  parent_id: null,
  position_x: 0,
  position_y: 0,
  position_z: 0,
  terrain: null,
}

export default function LocationsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: locations, isLoading, error } = useLocations(projectId!)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [showModal, setShowModal] = useState(false)
  const [editingLocation, setEditingLocation] = useState<Location | null>(null)
  const [formData, setFormData] = useState<LocationFormData>(emptyForm)

  // 构建层级树
  const locationTree = useMemo(() => {
    if (!locations) return []
    
    const locationMap = new Map<string, LocationWithChildren>()
    const roots: LocationWithChildren[] = []
    
    // 先创建所有节点
    locations.forEach(loc => {
      locationMap.set(loc.id, { ...loc, children: [] })
    })
    
    // 构建父子关系
    locations.forEach(loc => {
      const node = locationMap.get(loc.id)!
      if (loc.parent_id && locationMap.has(loc.parent_id)) {
        locationMap.get(loc.parent_id)!.children.push(node)
      } else {
        roots.push(node)
      }
    })
    
    // 按层级和位置排序
    const layerOrder = ['celestial', 'material', 'underworld', 'realm', 'void']
    roots.sort((a, b) => {
      const aIdx = layerOrder.indexOf(a.layer)
      const bIdx = layerOrder.indexOf(b.layer)
      if (aIdx !== bIdx) return aIdx - bIdx
      if (a.position_y !== b.position_y) return a.position_y - b.position_y
      return a.position_x - b.position_x
    })
    
    return roots
  }, [locations])

  // 递归渲染
  const renderLocation = (location: LocationWithChildren, level: number = 0) => {
    const hasChildren = location.children.length > 0
    const isExpanded = expandedIds.has(location.id)
    const terrainIcon = location.terrain ? TERRAIN_ICONS[location.terrain] || '📍' : '📍'
    
    return (
      <div key={location.id} className="mb-1">
        <div
          className={`flex items-center gap-2 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition ${
            level > 0 ? 'ml-8 border-l-2 border-indigo-200' : ''
          }`}
          style={{ marginLeft: level * 32 + 'px' }}
        >
          {/* 展开/折叠按钮 */}
          {hasChildren && (
            <button
              onClick={() => {
                const newExpanded = new Set(expandedIds)
                if (isExpanded) {
                  newExpanded.delete(location.id)
                } else {
                  newExpanded.add(location.id)
                }
                setExpandedIds(newExpanded)
              }}
              className="w-6 h-6 flex items-center justify-center text-gray-500 hover:text-gray-700"
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          {!hasChildren && <div className="w-6" />}
          
          {/* 图标 */}
          <span className="text-xl">{terrainIcon}</span>
          
          {/* 名称和描述 */}
          <div className="flex-1">
            <div className="font-medium text-gray-800">{location.name}</div>
            {location.description && (
              <div className="text-sm text-gray-500 truncate">{location.description}</div>
            )}
          </div>
          
          {/* 层级标签 */}
          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
            {LAYER_NAMES[location.layer] || location.layer}
          </span>
          
          {/* 坐标 */}
          <span className="text-xs text-gray-400">
            ({location.position_x}, {location.position_y})
          </span>
        </div>
        
        {/* 递归渲染子节点 */}
        {hasChildren && isExpanded && (
          <div className="mt-1">
            {location.children.map(child => renderLocation(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const openCreateModal = () => {
    setEditingLocation(null)
    setFormData(emptyForm)
    setShowModal(true)
  }

  const openEditModal = (location: Location) => {
    setEditingLocation(location)
    setFormData({
      name: location.name,
      description: location.description || '',
      layer: location.layer,
      parent_id: location.parent_id,
      position_x: location.position_x,
      position_y: location.position_y,
      position_z: location.position_z,
      terrain: location.terrain,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingLocation(null)
    setFormData(emptyForm)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">地点管理</h1>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          + 添加地点
        </button>
      </div>

      {/* 层级列表视图 */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">加载失败</div>
      ) : locationTree.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无地点，点击上方按钮添加第一个地点
        </div>
      ) : (
        <>
          <div className="space-y-1">
            {locationTree.map(location => renderLocation(location))}
          </div>
          {/* 手绘风格地图 */}
          {locations && locations.length > 0 && (
            <RoughMap locations={locations} />
          )}
        </>
      )}

      {/* 创建/编辑模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4">
              {editingLocation ? '编辑地点' : '添加地点'}
            </h2>
            <form>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    地点名称 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    空间层级
                  </label>
                  <select
                    value={formData.layer}
                    onChange={e => setFormData({ ...formData, layer: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="celestial">天界/神界</option>
                    <option value="material">人界/物质界</option>
                    <option value="underworld">冥界/地狱</option>
                    <option value="realm">秘境/异空间</option>
                    <option value="void">虚空</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    上级地点
                  </label>
                  <select
                    value={formData.parent_id || ''}
                    onChange={e => setFormData({ ...formData, parent_id: e.target.value || null })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">无（顶级地点）</option>
                    {locations?.filter(l => l.id !== editingLocation?.id).map(loc => (
                      <option key={loc.id} value={loc.id}>{loc.name}</option>
                    ))}
                  </select>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">X坐标</label>
                    <input
                      type="number"
                      value={formData.position_x}
                      onChange={e => setFormData({ ...formData, position_x: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Y坐标</label>
                    <input
                      type="number"
                      value={formData.position_y}
                      onChange={e => setFormData({ ...formData, position_y: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Z坐标</label>
                    <input
                      type="number"
                      value={formData.position_z}
                      onChange={e => setFormData({ ...formData, position_z: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    地点描述
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
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  {editingLocation ? '保存' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
