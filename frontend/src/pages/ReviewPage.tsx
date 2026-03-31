import { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  useForeshadowings,
  useForeshadowingStats,
  useCreateForeshadowing,
  useDeleteForeshadowing,
  useResolveForeshadowing,
  useExpireForeshadowing,
  Foreshadowing,
} from '../hooks/useForeshadowings'
import ChapterSelectList from '../components/ChapterSelectList'
import { useChapterReview, useTriggerFullReview, useApplyFix, ReviewResult, ReviewIssue } from '../hooks/useReviews'
import { useChapter } from '../hooks/useChapters'

type TabType = 'review' | 'foreshadowing'

export default function ReviewPage() {
  const { projectId, chapterId } = useParams()
  
  const [selectedChapterIds, setSelectedChapterIds] = useState<string[]>([])
  const [currentChapterId, setCurrentChapterId] = useState<string | null>(chapterId || null)
  const [activeTab, setActiveTab] = useState<TabType>('review')

  const { data: foreshadowingsData, isLoading: foreshadowingsLoading } = useForeshadowings(projectId!)
  const { data: statsData } = useForeshadowingStats(projectId!)
  const createForeshadowing = useCreateForeshadowing()
  const updateForeshadowing = useUpdateForeshadowing()
  const deleteForeshadowing = useDeleteForeshadowing()
  const resolveForeshadowing = useResolveForeshadowing()
  const expireForeshadowing = useExpireForeshadowing()

  const { data: chapter } = useChapter(projectId!, currentChapterId || '')
  const triggerReview = useTriggerFullReview()
  const applyFix = useApplyFix()
  
  const { data: reviewResult, isLoading: isReviewing } = useChapterReview(
    projectId!,
    currentChapterId || ''
  )

  const handleChapterSelect = (ids: string[]) => {
    setSelectedChapterIds(ids)
    if (ids.length === 1) {
      setCurrentChapterId(ids[0])
    }
  }

  const handleChapterClick = (id: string) => {
    setCurrentChapterId(id)
    setSelectedChapterIds([id])
  }

  const handleStartReview = async () => {
    if (!currentChapterId) return
    try {
      await triggerReview.mutateAsync({
        projectId: projectId!,
        chapterId: currentChapterId,
      })
    } catch (err) {
      console.error('审查失败:', err)
    }
  }

  const handleApplyFix = async (issue: ReviewIssue, index: number) => {
    if (!currentChapterId || !chapter) return
    try {
      await applyFix.mutateAsync({
        projectId: projectId!,
        chapterId: currentChapterId,
        issueIndex: index,
        fixedContent: issue.suggestion,
      })
    } catch (err) {
      console.error('应用修复失败:', err)
    }
  }

  const handleLocateIssue = (issue: ReviewIssue) => {
    console.log('定位问题:', issue.location)
  }

  const handleExport = (format: 'json' | 'markdown') => {
    if (!reviewResult) return

    let content: string
    let filename: string
    let mimeType: string

    if (format === 'json') {
      content = JSON.stringify(reviewResult, null, 2)
      filename = `review-report-${currentChapterId || 'chapter'}-${Date.now()}.json`
      mimeType = 'application/json'
    } else {
      content = generateMarkdownReport(reviewResult)
      filename = `review-report-${currentChapterId || 'chapter'}-${Date.now()}.md`
      mimeType = 'text/markdown'
    }

    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const generateMarkdownReport = (result: ReviewResult): string => {
    const scoreEmoji = result.score >= 8 ? '✅' : result.score >= 6 ? '⚠️' : '❌'
    let md = `# 审查报告\n\n`
    md += `## 综合评分\n\n`
    md += `${scoreEmoji} **${result.score.toFixed(1)}/10**\n\n`
    
    if (result.stats) {
      md += `### 统计信息\n\n`
      md += `- 字数：${result.stats.word_count?.toLocaleString() || 0}\n`
      md += `- 章节数：${result.stats.chapter_count || 0}\n`
      md += `- 矛盾问题：${result.stats.contradiction_count || 0}\n`
      md += `- OOC问题：${result.stats.ooc_count || 0}\n`
      md += `- 敏感词问题：${result.stats.sensitive_count || 0}\n\n`
    }

    md += `## 问题列表\n\n`
    
    if (result.issues && result.issues.length > 0) {
      result.issues.forEach((issue, index) => {
        const typeIcon = issue.type === 'contradiction' ? '⚠️' : issue.type === 'ooc' ? '👤' : '🔒'
        const severityText = issue.severity === 'high' ? '严重' : issue.severity === 'medium' ? '中等' : '轻微'
        
        md += `### ${index + 1}. ${typeIcon} ${issue.type === 'contradiction' ? '矛盾' : issue.type === 'ooc' ? 'OOC' : '敏感词'}\n\n`
        md += `- **严重程度**：${severityText}\n`
        md += `- **位置**：${issue.location}\n`
        md += `- **描述**：${issue.description}\n`
        md += `- **建议**：${issue.suggestion}\n\n`
      })
    } else {
      md += `✅ 暂无问题\n\n`
    }

    md += `---\n\n`
    md += `*报告生成时间：${new Date().toLocaleString('zh-CN')}*\n`
    
    return md
  }

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400'
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  // 伏笔管理相关
  const handleCreateForeshadowing = async () => {
    if (!currentChapterId) {
      alert('请先选择一个章节')
      return
    }
    const description = prompt('请输入伏笔描述：')
    if (!description) return
    const notes = prompt('请输入备注（可选）：') || undefined
    try {
      await createForeshadowing.mutateAsync({
        projectId: projectId!,
        chapterId: currentChapterId,
        description,
        notes,
      })
    } catch (err) {
      console.error('创建伏笔失败:', err)
    }
  }

  const handleResolveForeshadowing = async (foreshadowing: Foreshadowing) => {
    try {
      await resolveForeshadowing.mutateAsync({
        projectId: projectId!,
        foreshadowingId: foreshadowing.id,
      })
    } catch (err) {
      console.error('回收伏笔失败:', err)
    }
  }

  const handleExpireForeshadowing = async (foreshadowing: Foreshadowing) => {
    try {
      await expireForeshadowing.mutateAsync({
        projectId: projectId!,
        foreshadowingId: foreshadowing.id,
      })
    } catch (err) {
      console.error('标记伏笔失效失败:', err)
    }
  }

  const handleDeleteForeshadowing = async (foreshadowing: Foreshadowing) => {
    if (!confirm(`确定要删除伏笔"${foreshadowing.description}"吗？`)) return
    try {
      await deleteForeshadowing.mutateAsync({
        projectId: projectId!,
        foreshadowingId: foreshadowing.id,
      })
    } catch (err) {
      console.error('删除伏笔失败:', err)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planted': return 'bg-blue-100 text-blue-700'
      case 'resolved': return 'bg-green-100 text-green-700'
      case 'expired': return 'bg-gray-100 text-gray-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'planted': return '已埋下'
      case 'resolved': return '已回收'
      case 'expired': return '已失效'
      default: return status
    }
  }

  const foreshadowings = foreshadowingsData?.items || []

  return (
    <div className="flex h-full bg-gray-50">
      {/* 左侧：章节选择列表 */}
      <aside className="w-72 border-r bg-white flex-shrink-0 flex flex-col">
        <div className="p-3 border-b flex items-center justify-between">
          <span className="font-medium text-sm">章节列表</span>
        </div>
        <div className="flex-1 overflow-hidden">
          <ChapterSelectList
            projectId={projectId!}
            selectedChapterIds={selectedChapterIds}
            onSelectionChange={handleChapterSelect}
            onChapterClick={handleChapterClick}
          />
        </div>
      </aside>

      {/* 中间：主内容区域 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部工具栏 */}
        <div className="h-12 border-b bg-white flex items-center px-4 gap-2">
          {/* Tab 切换 */}
          <div className="flex border rounded overflow-hidden">
            <button
              onClick={() => setActiveTab('review')}
              className={`px-3 py-1 text-sm ${activeTab === 'review' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
            >
              📋 审查
            </button>
            <button
              onClick={() => setActiveTab('foreshadowing')}
              className={`px-3 py-1 text-sm ${activeTab === 'foreshadowing' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
            >
              🎯 伏笔 ({statsData?.total || 0})
            </button>
          </div>
          
          <div className="flex-1">
            {currentChapterId && chapter && (
              <span className="text-sm text-gray-600">
                当前章节：<span className="font-medium">{chapter.title || `第${chapter.sort_order}章`}</span>
              </span>
            )}
          </div>
          
          {/* 审查 Tab 专属 */}
          {activeTab === 'review' && (
            <>
              {/* 评分显示 */}
              {reviewResult && (
                <div className={`text-lg font-bold ${getScoreColor(reviewResult.score)}`}>
                  {reviewResult.score.toFixed(1)}
                </div>
              )}

              <button
                onClick={handleStartReview}
                disabled={!currentChapterId || isReviewing}
                className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isReviewing ? '审查中...' : '开始审查'}
              </button>

              {/* 导出按钮 */}
              {reviewResult && (
                <div className="relative group">
                  <button className="px-3 py-1.5 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors">
                    📥 导出
                  </button>
                  <div className="absolute right-0 mt-1 w-32 bg-white border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <button
                      onClick={() => handleExport('json')}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
                    >
                      JSON 格式
                    </button>
                    <button
                      onClick={() => handleExport('markdown')}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
                    >
                      Markdown 格式
                    </button>
                  </div>
                </div>
              )}
            </>
          )}

          {/* 伏笔 Tab 专属 */}
          {activeTab === 'foreshadowing' && (
            <button
              onClick={handleCreateForeshadowing}
              disabled={!currentChapterId}
              className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              + 添加伏笔
            </button>
          )}
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'review' ? (
            <ReviewResultPanel
              result={reviewResult as ReviewResult | null}
              isLoading={isReviewing}
              onApplyFix={handleApplyFix}
              onLocateIssue={handleLocateIssue}
              isApplying={applyFix.isPending}
            />
          ) : (
            <ForeshadowingPanel
              foreshadowings={foreshadowings}
              isLoading={foreshadowingsLoading}
              stats={statsData}
              currentChapterId={currentChapterId}
              onResolve={handleResolveForeshadowing}
              onExpire={handleExpireForeshadowing}
              onDelete={handleDeleteForeshadowing}
            />
          )}
        </div>
      </main>
    </div>
  )
}

// 审查结果面板组件（原有逻辑）
function ReviewResultPanel({
  result,
  isLoading,
  onApplyFix,
  onLocateIssue,
  isApplying,
}: {
  result: ReviewResult | null
  isLoading: boolean
  onApplyFix: (issue: ReviewIssue, index: number) => void
  onLocateIssue: (issue: ReviewIssue) => void
  isApplying: boolean
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-500">正在审查中...</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <div className="text-5xl mb-4">📋</div>
          <p>选择章节并点击「开始审查」</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto p-4">
      <div className="space-y-4">
        {result.issues?.map((issue, index) => (
          <div key={index} className="bg-white border rounded-lg p-4 shadow-sm">
            <div className="flex items-start gap-3">
              <span className="text-2xl">
                {issue.type === 'contradiction' ? '⚠️' : issue.type === 'ooc' ? '👤' : '🔒'}
              </span>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">
                    {issue.type === 'contradiction' ? '矛盾检测' : issue.type === 'ooc' ? 'OOC检测' : '敏感词'}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    issue.severity === 'high' ? 'bg-red-100 text-red-700' :
                    issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {issue.severity === 'high' ? '严重' : issue.severity === 'medium' ? '中等' : '轻微'}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{issue.description}</p>
                <div className="text-xs text-gray-400 mb-2">位置: {issue.location}</div>
                <div className="bg-blue-50 border border-blue-200 rounded p-2 text-sm mb-2">
                  <span className="text-blue-600">💡 建议: </span>
                  {issue.suggestion}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => onApplyFix(issue, index)}
                    disabled={isApplying}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    应用修复
                  </button>
                  <button
                    onClick={() => onLocateIssue(issue)}
                    className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded hover:bg-gray-200"
                  >
                    定位
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
        {!result.issues?.length && (
          <div className="text-center text-gray-400 py-8">
            <div className="text-5xl mb-4">✅</div>
            <p>暂无问题</p>
          </div>
        )}
      </div>
    </div>
  )
}

// 伏笔管理面板组件
function ForeshadowingPanel({
  foreshadowings,
  isLoading,
  stats,
  currentChapterId,
  onResolve,
  onExpire,
  onDelete,
}: {
  foreshadowings: Foreshadowing[]
  isLoading: boolean
  stats?: {
    total: number
    planted: number
    resolved: number
    expired: number
    resolution_rate: number
  }
  currentChapterId: string | null
  onResolve: (f: Foreshadowing) => void
  onExpire: (f: Foreshadowing) => void
  onDelete: (f: Foreshadowing) => void
}) {
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredForeshadowings = statusFilter === 'all'
    ? foreshadowings
    : foreshadowings.filter(f => f.status === statusFilter)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto p-4">
      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="bg-white border rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-gray-700">{stats.total}</div>
            <div className="text-xs text-gray-500">总伏笔数</div>
          </div>
          <div className="bg-white border rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-blue-600">{stats.planted}</div>
            <div className="text-xs text-gray-500">已埋下</div>
          </div>
          <div className="bg-white border rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-green-600">{stats.resolved}</div>
            <div className="text-xs text-gray-500">已回收</div>
          </div>
          <div className="bg-white border rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-green-600">{stats.resolution_rate}%</div>
            <div className="text-xs text-gray-500">回收率</div>
          </div>
        </div>
      )}

      {/* 筛选 */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-3 py-1 text-sm rounded ${statusFilter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600'}`}
        >
          全部
        </button>
        <button
          onClick={() => setStatusFilter('planted')}
          className={`px-3 py-1 text-sm rounded ${statusFilter === 'planted' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'}`}
        >
          已埋下
        </button>
        <button
          onClick={() => setStatusFilter('resolved')}
          className={`px-3 py-1 text-sm rounded ${statusFilter === 'resolved' ? 'bg-green-600 text-white' : 'bg-green-100 text-green-700'}`}
        >
          已回收
        </button>
        <button
          onClick={() => setStatusFilter('expired')}
          className={`px-3 py-1 text-sm rounded ${statusFilter === 'expired' ? 'bg-gray-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          已失效
        </button>
      </div>

      {/* 伏笔列表 */}
      {filteredForeshadowings.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <div className="text-5xl mb-4">🎯</div>
          <p>暂无伏笔</p>
          <p className="text-sm">点击「添加伏笔」创建第一个伏笔</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredForeshadowings.map((f) => (
            <div key={f.id} className="bg-white border rounded-lg p-4 shadow-sm">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🎯</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(f.status)}`}>
                      {getStatusText(f.status)}
                    </span>
                    <span className="text-xs text-gray-400">
                      章节: {f.chapter_id.substring(0, 8)}...
                    </span>
                  </div>
                  <p className="text-sm mb-2">{f.description}</p>
                  {f.notes && (
                    <p className="text-xs text-gray-500 mb-2 bg-gray-50 p-2 rounded">{f.notes}</p>
                  )}
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                    <span>埋下: {new Date(f.planted_at).toLocaleDateString('zh-CN')}</span>
                    {f.resolved_at && (
                      <span>回收: {new Date(f.resolved_at).toLocaleDateString('zh-CN')}</span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {f.status === 'planted' && (
                      <>
                        <button
                          onClick={() => onResolve(f)}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                        >
                          标记回收
                        </button>
                        <button
                          onClick={() => onExpire(f)}
                          className="px-3 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600"
                        >
                          标记失效
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => onDelete(f)}
                      className="px-3 py-1 bg-red-100 text-red-600 text-xs rounded hover:bg-red-200"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
