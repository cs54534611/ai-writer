interface AIFeedbackPanelProps {
  feedback: {
    score: number
    suggestions: string[]
  }
}

export default function AIFeedbackPanel({ feedback }: AIFeedbackPanelProps) {
  const scoreColor = feedback.score >= 7 ? 'text-green-600' : feedback.score >= 5 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="p-4 border-t">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium">AI 反馈</span>
        <span className={`text-lg font-bold ${scoreColor}`}>{feedback.score.toFixed(1)}</span>
      </div>
      
      {feedback.suggestions && feedback.suggestions.length > 0 ? (
        <ul className="space-y-2">
          {feedback.suggestions.map((s: string, i: number) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span className="text-purple-600 mt-0.5">•</span>
              <span className="text-gray-700">{s}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-gray-500">暂无建议</p>
      )}
    </div>
  )
}
