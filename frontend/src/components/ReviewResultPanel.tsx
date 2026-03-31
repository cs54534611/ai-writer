import { useState } from 'react'
import { ReviewIssue, ReviewResult } from '../hooks/useReviews'

interface ReviewResultPanelProps {
  result: ReviewResult | null
  isLoading: boolean
  onApplyFix: (issue: ReviewIssue, index: number) => void
  onLocateIssue: (issue: ReviewIssue) => void
  isApplying: boolean
}

type FilterType = 'all' | 'contradiction' | 'ooc' | 'sensitive'

export default function ReviewResultPanel({
  result,
  isLoading,
  onApplyFix,
  onLocateIssue,
  isApplying,
}: ReviewResultPanelProps) {
  const [filter, setFilter] = useState<FilterType>('all')

  const filteredIssues = result?.issues?.filter((issue) => {
    if (filter === 'all') return true
    return issue.type === filter
  }) || []

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 8) return 'bg-green-50 border-green-200'
    if (score >= 6) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-100'
      case 'medium':
        return 'text-orange-600 bg-orange-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'contradiction':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'ooc':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )
      case 'sensitive':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        )
      default:
        return null
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'contradiction':
        return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'ooc':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'sensitive':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getTypeName = (type: string) => {
    switch (type) {
      case 'contradiction':
        return '矛盾'
      case 'ooc':
        return 'OOC'
      case 'sensitive':
        return '敏感词'
      default:
        return type
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-3 text-sm text-gray-500">正在审查...</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">选择章节后点击"开始审查"</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 评分区域 */}
      <div className={`p-6 border-b ${getScoreBgColor(result.score)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">综合评分</p>
            <div className="flex items-baseline gap-2">
              <span className={`text-5xl font-bold ${getScoreColor(result.score)}`}>
                {result.score.toFixed(1)}
              </span>
              <span className="text-gray-400">/ 10</span>
            </div>
          </div>
          {/* 环形进度 */}
          <div className="relative w-20 h-20">
            <svg className="w-20 h-20 transform -rotate-90">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="currentColor"
                strokeWidth="6"
                fill="none"
                className="text-gray-200"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="currentColor"
                strokeWidth="6"
                fill="none"
                strokeDasharray={`${result.score * 22.6} 226`}
                strokeLinecap="round"
                className={getScoreColor(result.score)}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-lg font-bold ${getScoreColor(result.score)}`}>
                {Math.round(result.score * 10)}%
              </span>
            </div>
          </div>
        </div>

        {/* 统计信息 */}
        {result.stats && (
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="bg-white/60 rounded-lg p-2">
              <p className="text-xs text-gray-500">字数</p>
              <p className="text-sm font-medium">{result.stats.word_count?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-white/60 rounded-lg p-2">
              <p className="text-xs text-gray-500">章节</p>
              <p className="text-sm font-medium">{result.stats.chapter_count || 0}</p>
            </div>
          </div>
        )}
      </div>

      {/* 问题分类统计 */}
      <div className="px-4 py-3 border-b bg-gray-50 flex items-center gap-2 overflow-x-auto">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-100'
          }`}
        >
          全部 {result.issues?.length || 0}
        </button>
        <button
          onClick={() => setFilter('contradiction')}
          className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
            filter === 'contradiction'
              ? 'bg-orange-600 text-white'
              : 'bg-white text-orange-600 hover:bg-orange-50'
          }`}
        >
          ⚠ 矛盾 {result.issues?.filter(i => i.type === 'contradiction').length || 0}
        </button>
        <button
          onClick={() => setFilter('ooc')}
          className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
            filter === 'ooc'
              ? 'bg-yellow-600 text-white'
              : 'bg-white text-yellow-600 hover:bg-yellow-50'
          }`}
        >
          👤 OOC {result.issues?.filter(i => i.type === 'ooc').length || 0}
        </button>
        <button
          onClick={() => setFilter('sensitive')}
          className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
            filter === 'sensitive'
              ? 'bg-red-600 text-white'
              : 'bg-white text-red-600 hover:bg-red-50'
          }`}
        >
          🔒 敏感词 {result.issues?.filter(i => i.type === 'sensitive').length || 0}
        </button>
      </div>

      {/* 问题列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredIssues.length > 0 ? (
          filteredIssues.map((issue, index) => (
            <div
              key={index}
              className={`rounded-lg border p-4 ${getTypeColor(issue.type)}`}
            >
              {/* 问题头部 */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={issue.type === 'sensitive' ? 'text-red-600' : issue.type === 'ooc' ? 'text-yellow-600' : 'text-orange-600'}>
                    {getTypeIcon(issue.type)}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(issue.type)}`}>
                    {getTypeName(issue.type)}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                    {issue.severity === 'high' ? '严重' : issue.severity === 'medium' ? '中等' : '轻微'}
                  </span>
                </div>
                <span className="text-xs text-gray-400">{issue.location}</span>
              </div>

              {/* 问题描述 */}
              <p className="text-sm text-gray-700 mb-2">{issue.description}</p>

              {/* 修复建议 */}
              <div className="bg-white/60 rounded p-2 mb-3">
                <p className="text-xs text-gray-500 mb-1">建议修改</p>
                <p className="text-sm text-gray-700">{issue.suggestion}</p>
              </div>

              {/* 操作按钮 */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onLocateIssue(issue)}
                  className="flex-1 px-3 py-1.5 text-xs bg-white border border-gray-200 rounded hover:bg-gray-50 transition-colors"
                >
                  定位原文
                </button>
                <button
                  onClick={() => onApplyFix(issue, index)}
                  disabled={isApplying}
                  className="flex-1 px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isApplying ? '应用中...' : '应用建议'}
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 py-12">
            <svg className="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm">
              {filter === 'all' ? '暂无问题' : `暂无${getTypeName(filter)}问题`}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
