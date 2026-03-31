import { useNavigate, useParams } from 'react-router-dom'

interface JourneyStage {
  id: string
  label: string
  icon: string
  progress: number
  nextAction?: string
  path: string
}

interface CreativeJourneyProps {
  projectId: string
  className?: string
}

export default function CreativeJourney({ projectId, className = '' }: CreativeJourneyProps) {
  const navigate = useNavigate()

  // In a real app, these would come from hooks querying project state
  const stages: JourneyStage[] = [
    {
      id: 'inspirations',
      label: '灵感收集',
      icon: '💡',
      progress: 0,
      nextAction: '添加灵感素材',
      path: `/projects/${projectId}/inspirations`,
    },
    {
      id: 'outline',
      label: '大纲规划',
      icon: '📋',
      progress: 0,
      nextAction: '创建故事大纲',
      path: `/projects/${projectId}/writing`,
    },
    {
      id: 'writing',
      label: '正文撰写',
      icon: '✍️',
      progress: 0,
      nextAction: '开始写作',
      path: `/projects/${projectId}/writing`,
    },
    {
      id: 'review',
      label: '阅读审查',
      icon: '🔍',
      progress: 0,
      nextAction: 'AI 审查润色',
      path: `/projects/${projectId}/review`,
    },
  ]

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'bg-green-500'
    if (progress >= 50) return 'bg-blue-500'
    return 'bg-purple-500'
  }

  const getStageBgColor = (progress: number) => {
    if (progress >= 100) return 'bg-green-50 border-green-200'
    if (progress >= 50) return 'bg-blue-50 border-blue-200'
    return 'bg-gray-50 border-gray-200'
  }

  return (
    <div className={`bg-white rounded-xl p-6 shadow-sm ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-6">创作旅程</h3>
      <div className="relative">
        {/* Progress Line */}
        <div className="absolute top-8 left-0 right-0 h-1 bg-gray-200 rounded-full" />
        <div
          className="absolute top-8 left-0 h-1 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
          style={{ width: '25%' }}
        />

        {/* Stages */}
        <div className="grid grid-cols-4 gap-4 relative">
          {stages.map((stage, index) => (
            <div key={stage.id} className="flex flex-col items-center">
              {/* Stage Circle */}
              <button
                onClick={() => navigate(stage.path)}
                className={`relative z-10 w-16 h-16 rounded-full border-4 ${getStageBgColor(stage.progress)} ${getProgressColor(stage.progress)} transition-all hover:scale-105`}
              >
                <span className="absolute inset-0 flex items-center justify-center text-2xl">
                  {stage.progress >= 100 ? '✓' : stage.icon}
                </span>
                {stage.progress > 0 && stage.progress < 100 && (
                  <span
                    className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-white border-2 flex items-center justify-center text-xs font-bold text-blue-600 shadow-sm"
                  >
                    {stage.progress}%
                  </span>
                )}
              </button>

              {/* Label */}
              <span className="mt-3 text-sm font-medium text-gray-700 text-center">
                {stage.label}
              </span>

              {/* Next Action */}
              {stage.progress < 100 && stage.nextAction && (
                <button
                  onClick={() => navigate(stage.path)}
                  className="mt-2 text-xs text-blue-600 hover:text-blue-700 hover:underline"
                >
                  {stage.nextAction}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Overall Progress */}
      <div className="mt-8 pt-6 border-t border-gray-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">整体完成度</span>
          <span className="text-sm font-semibold text-gray-900">0%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
            style={{ width: '0%' }}
          />
        </div>
      </div>
    </div>
  )
}
