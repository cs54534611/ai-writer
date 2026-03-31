import { useState, useRef, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useRelationshipGraph, useRelationships, useCreateRelationship, useDeleteRelationship } from '../hooks/useRelationships'
import { useCharacters } from '../hooks/useCharacters'
import type { Character } from '../types'

interface NodePosition {
  id: string
  x: number
  y: number
  vx?: number
  vy?: number
}

interface GraphNode extends NodePosition {
  id: string
  name: string
  gender?: string
}

const NODE_RADIUS = 30
// 关系类型筛选配置
const RELATIONSHIP_FILTER_TYPES = [
  { key: 'all', label: '全部', color: '#6b7280' },
  { key: 'family', label: '亲情', color: '#3b82f6' },
  { key: 'friend', label: '友情', color: '#22c55e' },
  { key: 'love', label: '爱情', color: '#ec4899' },
  { key: 'enemy', label: '对立', color: '#ef4444' },
  { key: 'subordinate', label: '从属', color: '#a855f7' },
]

// 关系类型映射到筛选类别
const RELATION_TYPE_MAP: Record<string, string> = {
  '家人': 'family',
  '亲人': 'family',
  '父子': 'family',
  '母子': 'family',
  '兄弟': 'family',
  '姐妹': 'family',
  '朋友': 'friend',
  '闺蜜': 'friend',
  '恋人': 'love',
  '情侣': 'love',
  '爱人': 'love',
  '敌人': 'enemy',
  '仇人': 'enemy',
  '对手': 'enemy',
  '同事': 'subordinate',
  '上下级': 'subordinate',
  '师生': 'subordinate',
  '主仆': 'subordinate',
}

export default function RelationshipGraph() {
  const { projectId } = useParams<{ projectId: string }>()
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const [viewBox, setViewBox] = useState({ x: 0, y: 0, width: 800, height: 600 })
  const [isDragging, setIsDragging] = useState(false)
  const [draggedNode, setDraggedNode] = useState<string | null>(null)
  const [lastMouse, setLastMouse] = useState({ x: 0, y: 0 })
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [relationshipFilter, setRelationshipFilter] = useState('all')
  const [showAddRelation, setShowAddRelation] = useState(false)
  const [relationForm, setRelationForm] = useState({
    sourceId: '',
    targetId: '',
    relationshipType: '朋友',
    description: '',
  })

  const { data: graphData, isLoading, error } = useRelationshipGraph(projectId!)
  const { data: characters } = useCharacters(projectId!)
  const { data: relationships } = useRelationships(projectId!)
  const createRelationship = useCreateRelationship()
  const deleteRelationship = useDeleteRelationship()

  // Initialize node positions
  const [nodes, setNodes] = useState<Map<string, NodePosition>>(new Map())

  useEffect(() => {
    if (graphData?.nodes && graphData.nodes.length > 0) {
      const centerX = viewBox.width / 2
      const centerY = viewBox.height / 2
      const radius = Math.min(viewBox.width, viewBox.height) / 3

      const newNodes = new Map<string, NodePosition>()
      graphData.nodes.forEach((node, index) => {
        const angle = (2 * Math.PI * index) / graphData.nodes!.length
        newNodes.set(node.id, {
          id: node.id,
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        })
      })
      setNodes(newNodes)
    }
  }, [graphData])

  // Simple force simulation
  useEffect(() => {
    if (!graphData?.nodes || graphData.nodes.length === 0) return

    const simulation = () => {
      setNodes(prevNodes => {
        const newNodes = new Map(prevNodes)
        const nodesArray = Array.from(newNodes.values())

        // Repulsion between nodes
        for (let i = 0; i < nodesArray.length; i++) {
          for (let j = i + 1; j < nodesArray.length; j++) {
            const a = nodesArray[i]
            const b = nodesArray[j]
            const dx = b.x - a.x
            const dy = b.y - a.y
            const dist = Math.sqrt(dx * dx + dy * dy) || 1
            const force = 1000 / (dist * dist)

            const fx = (dx / dist) * force
            const fy = (dy / dist) * force

            newNodes.get(a.id)!.vx = (newNodes.get(a.id)!.vx || 0) - fx
            newNodes.get(a.id)!.vy = (newNodes.get(a.id)!.vy || 0) - fy
            newNodes.get(b.id)!.vx = (newNodes.get(b.id)!.vx || 0) + fx
            newNodes.get(b.id)!.vy = (newNodes.get(b.id)!.vy || 0) + fy
          }
        }

        // Attraction along edges
        if (graphData.links) {
          for (const link of graphData.links) {
            const source = newNodes.get(link.source as string)
            const target = newNodes.get(link.target as string)
            if (source && target) {
              const dx = target.x - source.x
              const dy = target.y - source.y
              const dist = Math.sqrt(dx * dx + dy * dy) || 1
              const force = (dist - 150) * 0.01

              const fx = (dx / dist) * force
              const fy = (dy / dist) * force

              source.vx = (source.vx || 0) + fx
              source.vy = (source.vy || 0) + fy
              target.vx = (target.vx || 0) - fx
              target.vy = (target.vy || 0) - fy
            }
          }
        }

        // Center gravity
        const centerX = viewBox.width / 2
        const centerY = viewBox.height / 2
        for (const node of nodesArray) {
          node.vx = (node.vx || 0) + (centerX - node.x) * 0.001
          node.vy = (node.vy || 0) + (centerY - node.y) * 0.001

          // Apply velocity with damping
          node.x += node.vx! * 0.5
          node.y += node.vy! * 0.5
          node.vx! *= 0.9
          node.vy! *= 0.9

          // Boundary
          node.x = Math.max(NODE_RADIUS, Math.min(viewBox.width - NODE_RADIUS, node.x))
          node.y = Math.max(NODE_RADIUS, Math.min(viewBox.height - NODE_RADIUS, node.y))
        }

        return newNodes
      })
    }

    const interval = setInterval(simulation, 50)
    return () => clearInterval(interval)
  }, [graphData, viewBox])

  const handleMouseDown = (e: React.MouseEvent, nodeId?: string) => {
    if (nodeId) {
      setDraggedNode(nodeId)
    } else {
      setIsDragging(true)
    }
    setLastMouse({ x: e.clientX, y: e.clientY })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggedNode && nodes.has(draggedNode)) {
      const scale = viewBox.width / (containerRef.current?.clientWidth || 800)
      const dx = (e.clientX - lastMouse.x) * scale
      const dy = (e.clientY - lastMouse.y) * scale

      setNodes(prev => {
        const newNodes = new Map(prev)
        const node = newNodes.get(draggedNode)!
        newNodes.set(draggedNode, { ...node, x: node.x + dx, y: node.y + dy, vx: 0, vy: 0 })
        return newNodes
      })
    } else if (isDragging) {
      const scale = viewBox.width / (containerRef.current?.clientWidth || 800)
      const dx = (e.clientX - lastMouse.x) * scale
      const dy = (e.clientY - lastMouse.y) * scale

      setViewBox(prev => ({
        ...prev,
        x: prev.x - dx,
        y: prev.y - dy,
      }))
    }
    setLastMouse({ x: e.clientX, y: e.clientY })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setDraggedNode(null)
  }

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const scale = e.deltaY > 0 ? 1.1 : 0.9
    const newWidth = viewBox.width * scale
    const newHeight = viewBox.height * scale

    if (newWidth > 200 && newWidth < 2000) {
      const mouseX = e.nativeEvent.offsetX
      const mouseY = e.nativeEvent.offsetY
      const ratioX = mouseX / (containerRef.current?.clientWidth || 800)
      const ratioY = mouseY / (containerRef.current?.clientHeight || 600)

      setViewBox(prev => ({
        x: prev.x + (prev.width - newWidth) * ratioX,
        y: prev.y + (prev.height - newHeight) * ratioY,
        width: newWidth,
        height: newHeight,
      }))
    }
  }

  const handleNodeClick = (e: React.MouseEvent, node: GraphNode) => {
    e.stopPropagation()
    setSelectedNode(node)
  }

  const handleAddRelationship = async () => {
    if (!projectId || !relationForm.sourceId || !relationForm.targetId) return

    try {
      await createRelationship.mutateAsync({
        project_id: projectId,
        from_character_id: relationForm.sourceId,
        to_character_id: relationForm.targetId,
        relation_type: relationForm.relationshipType,
      } as any)
      setShowAddRelation(false)
      setRelationForm({ sourceId: '', targetId: '', relationshipType: '朋友', description: '' })
    } catch (err) {
      console.error('Failed to create relationship:', err)
    }
  }

  const handleDeleteRelationship = async (id: string) => {
    if (!confirm('确定要删除这段关系吗？')) return
    try {
      await deleteRelationship.mutateAsync({ id, projectId: projectId! })
    } catch (err) {
      console.error('Failed to delete relationship:', err)
    }
  }

  const getNodeColor = (gender?: string) => {
    switch (gender) {
      case 'male': return '#60a5fa' // blue
      case 'female': return '#f472b6' // pink
      default: return '#a78bfa' // purple
    }
  }

  const getCharacterById = (id: string): Character | undefined => {
    return characters?.find(c => c.id === id)
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
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">关系图谱</h2>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setRelationForm({ sourceId: '', targetId: '', relationshipType: '朋友', description: '' })
              setShowAddRelation(true)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + 添加关系
          </button>
        </div>
      </div>

      {/* 关系类型筛选 Tab */}
      <div className="flex gap-2 mb-4">
        {RELATIONSHIP_FILTER_TYPES.map(filter => (
          <button
            key={filter.key}
            onClick={() => setRelationshipFilter(filter.key)}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
              relationshipFilter === filter.key
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            style={relationshipFilter === filter.key ? { backgroundColor: filter.color } : {}}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="flex-1 bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
        <div
          ref={containerRef}
          className="w-full h-full cursor-grab active:cursor-grabbing"
          onMouseDown={(e) => handleMouseDown(e)}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
          >
            {/* Render links */}
            {graphData?.links?.map((link, index) => {
              const source = nodes.get(link.source as string)
              const target = nodes.get(link.target as string)
              if (!source || !target) return null

              // 筛选逻辑：关系类型过滤
              const linkTypeKey = RELATION_TYPE_MAP[link.type] || 'other'
              const isFiltered = relationshipFilter !== 'all' && linkTypeKey !== relationshipFilter

              // 高亮逻辑：选中节点时只显示该节点相关的关系
              const isRelatedToSelected = selectedNode && 
                (link.source === selectedNode.id || link.target === selectedNode.id)
              const isHighlighted = selectedNode && isRelatedToSelected
              const isDimmed = selectedNode && !isRelatedToSelected

              // 如果被过滤则不显示
              if (isFiltered) return null

              const dx = target.x - source.x
              const dy = target.y - source.y
              const dist = Math.sqrt(dx * dx + dy * dy) || 1
              const angle = Math.atan2(dy, dx)

              // Position arrow before target node
              const arrowX = target.x - (NODE_RADIUS + 5) * (dx / dist)
              const arrowY = target.y - (NODE_RADIUS + 5) * (dy / dist)

              // 关系线颜色
              const linkColor = isHighlighted ? '#2563eb' : (isDimmed ? '#d1d5db' : '#9ca3af')
              const linkWidth = isHighlighted ? 3 : 2

              return (
                <g key={`link-${index}`}>
                  <line
                    x1={source.x}
                    y1={source.y}
                    x2={arrowX}
                    y2={arrowY}
                    stroke={linkColor}
                    strokeWidth={linkWidth}
                    style={{ opacity: isDimmed ? 0.3 : 1 }}
                  />
                  {/* Arrow head */}
                  <polygon
                    points="0,-5 10,0 0,5"
                    fill={linkColor}
                    transform={`translate(${arrowX},${arrowY}) rotate(${((angle * 180) / Math.PI).toFixed(2)})`}
                    style={{ opacity: isDimmed ? 0.3 : 1 }}
                  />
                  {/* Relationship label */}
                  <text
                    x={(source.x + target.x) / 2}
                    y={(source.y + target.y) / 2 - 10}
                    textAnchor="middle"
                    className="text-xs fill-gray-600 pointer-events-none"
                    style={{ fontSize: '12px', opacity: isDimmed ? 0.3 : 1 }}
                  >
                    {link.type}
                  </text>
                </g>
              )
            })}

            {/* Render nodes */}
            {graphData?.nodes?.map((node) => {
              const pos = nodes.get(node.id)
              if (!pos) return null

              // 高亮/淡化逻辑
              const isRelatedToSelected = selectedNode && relationships?.some(
                r => (r.source_id === selectedNode.id && r.target_id === node.id) ||
                     (r.target_id === selectedNode.id && r.source_id === node.id)
              )
              const isHighlighted = selectedNode?.id === node.id || isRelatedToSelected
              const isDimmed = selectedNode && !isHighlighted

              return (
                <g
                  key={node.id}
                  onClick={(e) => handleNodeClick(e, { ...node, x: pos.x, y: pos.y })}
                  style={{ cursor: 'pointer', opacity: isDimmed ? 0.3 : 1 }}
                >
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={selectedNode?.id === node.id ? NODE_RADIUS + 5 : NODE_RADIUS}
                    fill={getNodeColor(node.gender)}
                    stroke={selectedNode?.id === node.id ? '#2563eb' : '#fff'}
                    strokeWidth={selectedNode?.id === node.id ? 4 : 2}
                  />
                  <text
                    x={pos.x}
                    y={pos.y + 4}
                    textAnchor="middle"
                    className="text-sm font-medium fill-white pointer-events-none"
                    style={{ fontSize: '14px' }}
                  >
                    {node.name.slice(0, 4)}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>

      {/* Selected Node Panel */}
      {selectedNode && (
        <div className="fixed right-8 top-1/2 transform -translate-y-1/2 w-64 bg-white rounded-lg shadow-lg p-4 border border-gray-200">
          <div className="flex justify-between items-start mb-3">
            <h3 className="font-semibold text-gray-900">{selectedNode.name}</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-500 mb-3">
            {selectedNode.gender === 'male' ? '男' : selectedNode.gender === 'female' ? '女' : '未设置'}
          </p>
          <div className="border-t border-gray-200 pt-3">
            <h4 className="text-sm font-medium text-gray-700 mb-2">关系</h4>
            {relationships?.filter(r => r.source_id === selectedNode.id || r.target_id === selectedNode.id).map(r => {
              const otherId = r.source_id === selectedNode.id ? r.target_id : r.source_id
              const other = getCharacterById(otherId)
              return (
                <div key={r.id} className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">
                    {r.source_id === selectedNode.id ? '→ ' : '← '}
                    {other?.name || '未知'} ({r.relationship_type})
                  </span>
                  <button
                    onClick={() => handleDeleteRelationship(r.id)}
                    className="text-red-500 hover:text-red-700 text-xs"
                  >
                    删除
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Add Relationship Modal */}
      {showAddRelation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">添加关系</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">角色 A</label>
                <select
                  value={relationForm.sourceId}
                  onChange={(e) => setRelationForm({ ...relationForm, sourceId: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">选择角色</option>
                  {characters?.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">关系类型</label>
                <select
                  value={relationForm.relationshipType}
                  onChange={(e) => setRelationForm({ ...relationForm, relationshipType: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {RELATIONSHIP_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">角色 B</label>
                <select
                  value={relationForm.targetId}
                  onChange={(e) => setRelationForm({ ...relationForm, targetId: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">选择角色</option>
                  {characters?.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  value={relationForm.description}
                  onChange={(e) => setRelationForm({ ...relationForm, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowAddRelation(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                取消
              </button>
              <button
                onClick={handleAddRelationship}
                disabled={!relationForm.sourceId || !relationForm.targetId || createRelationship.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createRelationship.isPending ? '添加中...' : '添加'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
