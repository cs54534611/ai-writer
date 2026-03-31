import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useChapter } from '../hooks/useChapters'
import { useTriggerFullReview, useChapterReview, useApplyFix, ReviewResult, ReviewIssue } from '../hooks/useReviews'
import ChapterSelectList from '../components/ChapterSelectList'
import ReviewResultPanel from '../components/ReviewResultPanel'

export default function ReviewPage() {
  const { projectId, chapterId } = useParams()
  const navigate = useNavigate()
  
  const [selectedChapterIds, setSelectedChapterIds] = useState<string[]>([])
  const [currentChapterId, setCurrentChapterId] = useState<string | null>(chapterId || null)
  const [exportFormat, setExportFormat] = useState<'json' | 'markdown' | null>(null)
  
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
    // TODO: 跳转到 WritingPage 并定位到问题位置
    console.log('定位问题:', issue.location)
    // navigate(`/projects/${projectId}/writing/chapters/${currentChapterId}?location=${encodeURIComponent(issue.location)}`)
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

  const reviewedCount = 0 // TODO: 从章节列表中计算

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

      {/* 中间：审查结果面板 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部工具栏 */}
        <div className="h-12 border-b bg-white flex items-center px-4 gap-2">
          <div className="flex-1">
            {currentChapterId && chapter && (
              <span className="text-sm text-gray-600">
                当前章节：<span className="font-medium">{chapter.title || `第${chapter.sort_order}章`}</span>
              </span>
            )}
          </div>
          
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
        </div>

        {/* 审查结果 */}
        <div className="flex-1 overflow-hidden">
          <ReviewResultPanel
            result={reviewResult as ReviewResult | null}
            isLoading={isReviewing}
            onApplyFix={handleApplyFix}
            onLocateIssue={handleLocateIssue}
            isApplying={applyFix.isPending}
          />
        </div>
      </main>
    </div>
  )
}
