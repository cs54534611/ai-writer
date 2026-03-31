import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useProject } from '../hooks/useProjects'
import { useChapters } from '../hooks/useChapters'
import { useCharacters } from '../hooks/useCharacters'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts'

const STAGES = [
  { key: 'inspiration', label: '灵感收集', color: 'bg-purple-500' },
  { key: 'outline', label: '大纲规划', color: 'bg-blue-500' },
  { key: 'writing', label: '正文撰写', color: 'bg-green-500' },
  { key: 'review', label: '阅读审查', color: 'bg-orange-500' },
]

export default function DashboardPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { data: project } = useProject(projectId!)
  const { data: chapters } = useChapters(projectId!)
  const { data: characters } = useCharacters(projectId!)

  const totalWords = chapters?.reduce((s, c) => s + (c.word_count || 0), 0) || 0
  const target = project?.total_words_target || 100000
  const progress = Math.min(100, Math.round((totalWords / target) * 100))
  const completedChapters = chapters?.filter(c => c.status === 'completed' || c.status === 'reviewed').length || 0

  // 近7天写作数据（模拟数据，实际应从API获取）
  const chartData = useMemo(() => {
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const today = new Date().getDay()
    const weekData = []
    // 计算每日平均目标
    const dailyTarget = 3000
    
    for (let i = 6; i >= 0; i--) {
      const dayIndex = (today - i + 7) % 7
      // 模拟每天的字数：取章节内容估算
      const wordsWritten = chapters?.length ? 
        Math.floor((chapters.reduce((s, c) => s + (c.word_count || 0), 0) / Math.max(1, chapters.length)) * (0.5 + Math.random())) 
        : Math.floor(Math.random() * 2000)
      
      // 计算累计进度
      const cumulativeWords = i === 0 ? totalWords : Math.floor(totalWords * (6 - i) / 6 + Math.random() * 500)
      // 每日写作字数（用累计差值估算）
      const dailyWords = i === 0 ? Math.floor(totalWords * 0.1) : Math.floor(Math.random() * 2000 + 500)
      
      weekData.push({
        day: days[dayIndex],
        '今日写作': dailyWords,
        '已写字数': cumulativeWords,
        '目标字数': dailyTarget,
        '7日平均': Math.floor(dailyTarget * 0.8), // 模拟7日平均
      })
    }
    return weekData
  }, [chapters, totalWords])

  const suggestions = [
    { text: '完善角色设定', action: () => navigate(`/projects/${projectId}/characters`), icon: '👤' },
    { text: '生成故事大纲', action: () => navigate(`/projects/${projectId}/outlines`), icon: '📋' },
    { text: '开始写作', action: () => navigate(`/projects/${projectId}/writing`), icon: '✍️' },
    { text: '审查章节', action: () => navigate(`/projects/${projectId}/review`), icon: '🔍' },
  ]

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">创作旅程仪表盘</h2>

      {/* 进度卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-gray-500 text-sm mb-1">写作进度</p>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold text-blue-600">{progress}%</span>
            <span className="text-sm text-gray-400 mb-1">{totalWords.toLocaleString()} / {target.toLocaleString()} 字</span>
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full">
            <div className="h-2 bg-blue-500 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-gray-500 text-sm mb-1">章节进度</p>
          <span className="text-3xl font-bold text-green-600">{completedChapters}</span>
          <span className="text-gray-400 ml-1">/ {chapters?.length || 0} 章完成</span>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <p className="text-gray-500 text-sm mb-1">角色数量</p>
          <span className="text-3xl font-bold text-purple-600">{characters?.length || 0}</span>
          <span className="text-gray-400 ml-1">个角色</span>
        </div>
      </div>

      {/* 创作旅程 */}
      <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
        <h3 className="font-semibold mb-4">创作旅程</h3>
        <div className="flex items-center gap-2">
          {STAGES.map((stage, i) => {
            // 进度计算：每阶段基于合理阈值
            const stageProgress = (() => {
              switch (stage.key) {
                case 'writing': return progress
                case 'outline': {
                  // 有大纲节点就算 50%+，每多一个节点加一点
                  const outlineCount = chapters?.length || 0
                  return outlineCount === 0 ? 0 : Math.min(95, 30 + outlineCount * 5)
                }
                case 'review': {
                  // 基于已完成章节比例
                  const total = chapters?.length || 0
                  return total === 0 ? 0 : Math.round((completedChapters / total) * 100)
                }
                case 'inspiration': {
                  // 基于角色数量：有角色说明在建立世界观
                  const count = characters?.length || 0
                  return count === 0 ? 0 : Math.min(90, count * 15)
                }
                default: return 0
              }
            })()
            return (
              <div key={stage.key} className="flex items-center gap-2">
                {i > 0 && <div className="flex-1 h-1 bg-gray-200 rounded" />}
                <div className="flex flex-col items-center gap-1">
                  <div className={`w-12 h-12 rounded-full ${stage.color} flex items-center justify-center text-white text-xl`}>
                    {stageProgress >= 50 ? '✓' : '○'}
                  </div>
                  <span className="text-xs text-gray-500">{stage.label}</span>
                  <span className="text-xs font-medium">{Math.min(100, stageProgress)}%</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* AI 建议 */}
      <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
        <h3 className="font-semibold mb-4">✨ AI 建议</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={s.action}
              className="p-4 border rounded-lg hover:border-blue-500 hover:bg-blue-50 text-left transition-all"
            >
              <span className="text-xl">{s.icon}</span>
              <p className="text-sm font-medium mt-1">{s.text}</p>
            </button>
          ))}
        </div>
      </div>

      {/* 写作趋势图表 */}
      <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">📊 近7天写作趋势</h3>
          <div className="flex gap-4 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-blue-500"></span> 今日写作
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-green-400"></span> 7日平均
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-0.5 bg-red-400" style={{borderStyle: 'dashed'}}></span> 日目标3000字
            </span>
          </div>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                formatter={(value: number, name: string) => [`${value.toLocaleString()} 字`, name]}
              />
              <Legend />
              <ReferenceLine y={3000} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={1.5} label={{ value: '日目标', position: 'right', fill: '#ef4444', fontSize: 10 }} />
              <Bar dataKey="今日写作" name="今日写作" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="7日平均" name="7日平均" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 最近章节 */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h3 className="font-semibold mb-4">最近章节</h3>
        {(chapters || []).slice(0, 5).map(c => (
          <div key={c.id} className="flex items-center justify-between py-2 border-b last:border-0">
            <div>
              <p className="font-medium">{c.title}</p>
              <p className="text-xs text-gray-400">{c.word_count.toLocaleString()} 字</p>
            </div>
            <span className={`text-xs px-2 py-1 rounded ${
              c.status === 'completed' ? 'bg-green-100 text-green-700'
              : c.status === 'reviewed' ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-600'
            }`}>{c.status}</span>
          </div>
        ))}
        {(!chapters || chapters.length === 0) && (
          <p className="text-gray-400 text-center py-4">暂无章节</p>
        )}
      </div>
    </div>
  )
}
