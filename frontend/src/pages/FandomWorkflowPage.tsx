import { useState } from 'react'
import { useParams } from 'react-router-dom'

export default function FandomWorkflowPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [step, setStep] = useState(1)
  const [sourceText, setSourceText] = useState('')
  const [importResult, setImportResult] = useState<any>(null)
  const [selectedChars, setSelectedChars] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [outlineResult, setOutlineResult] = useState<any>(null)

  const handleImport = async () => {
    if (!sourceText.trim()) return
    setIsLoading(true)
    try {
      const res = await fetch(`/api/v1/projects/${projectId}/fandom/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_text: sourceText }),
      })
      if (res.ok) {
        const data = await res.json()
        setImportResult(data)
        setStep(2)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateOutline = async () => {
    setIsLoading(true)
    try {
      const res = await fetch(`/api/v1/projects/${projectId}/fandom/outline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fandom_name: importResult.fandom_name || '',
          character_ids: selectedChars,
          relationship_summary: importResult.relationship_summary || '',
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setOutlineResult(data)
        setStep(3)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">同人创作工作流</h2>

      {/* 步骤指示器 */}
      <div className="flex items-center mb-8">
        {[1, 2, 3].map(n => (
          <div key={n} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
              step >= n ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
            }`}>{n}</div>
            <span className="ml-2 text-sm">{n === 1 ? '导入原文' : n === 2 ? '选择角色' : '生成大纲'}</span>
            {n < 3 && <div className="w-16 h-0.5 bg-gray-200 mx-4" />}
          </div>
        ))}
      </div>

      {/* Step 1: 导入 */}
      {step === 1 && (
        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold mb-4">粘贴原文小说文本</h3>
          <textarea
            value={sourceText}
            onChange={e => setSourceText(e.target.value)}
            rows={10}
            placeholder="粘贴你想分析的小说文本，AI 将提取角色、世界观和叙事风格..."
            className="w-full border rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-400 mt-2">字数越多分析越准确，建议至少 5000 字</p>
          <button
            onClick={handleImport}
            disabled={!sourceText.trim() || isLoading}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? '分析中...' : '开始分析'}
          </button>
        </div>
      )}

      {/* Step 2: 选择角色 */}
      {step === 2 && importResult && (
        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold mb-4">提取结果</h3>
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium">世界观：{importResult.world_settings?.slice(0, 3).join('、')}</p>
            <p className="text-sm text-gray-500 mt-1">提取到 {importResult.characters?.length || 0} 个角色</p>
          </div>
          <h4 className="font-medium mb-2">选择要延展的角色</h4>
          <div className="flex flex-wrap gap-2 mb-4">
            {(importResult.characters || []).map((c: any, i: number) => (
              <button
                key={i}
                onClick={() => setSelectedChars(prev => prev.includes(c.name) ? prev.filter(x => x !== c.name) : [...prev, c.name])}
                className={`px-3 py-1.5 border rounded-full text-sm ${
                  selectedChars.includes(c.name) ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200'
                }`}
              >
                {c.name}
              </button>
            ))}
          </div>
          <button
            onClick={handleGenerateOutline}
            disabled={selectedChars.length === 0 || isLoading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {isLoading ? '生成中...' : '✨ 生成同人大纲'}
          </button>
        </div>
      )}

      {/* Step 3: 大纲结果 */}
      {step === 3 && outlineResult && (
        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold mb-4">同人创作大纲</h3>
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto">
              {outlineResult.outline || JSON.stringify(outlineResult, null, 2)}
            </pre>
          </div>
          <button
            onClick={() => { setStep(1); setSourceText(''); setImportResult(null); setOutlineResult(null); setSelectedChars([]) }}
            className="mt-4 px-6 py-2 bg-gray-200 text-gray-700 rounded-lg"
          >
            重新开始
          </button>
        </div>
      )}
    </div>
  )
}
