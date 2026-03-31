import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useCharacters } from '../hooks/useCharacters'

const STYLES = [
  { value: 'anime', label: '动漫风' },
  { value: 'realistic', label: '写实风' },
  { value: 'ink', label: '水墨风' },
  { value: 'watercolor', label: '水彩风' },
]

const SIZES = ['512x512', '1024x1024']

export default function ImageGalleryPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: characters } = useCharacters(projectId!)
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('anime')
  const [size, setSize] = useState('512x512')
  const [selectedChars, setSelectedChars] = useState<string[]>([])
  const [images, setImages] = useState<{ url: string; prompt: string; char?: string }[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setIsGenerating(true)
    try {
      const charNames = selectedChars.map(id => characters?.find(c => c.id === id)?.name).filter(Boolean).join(', ')
      const enhancedPrompt = charNames ? `${prompt}, ${charNames}` : prompt
      const res = await fetch(`/api/v1/projects/${projectId}/images/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: enhancedPrompt, style, size, character_ids: selectedChars }),
      })
      if (res.ok) {
        const data = await res.json()
        const imgUrl = data.b64_json ? `data:image/png;base64,${data.b64_json}` : data.url
        setImages(prev => [{ url: imgUrl, prompt: enhancedPrompt, char: charNames }, ...prev])
        setPreview(imgUrl)
      }
    } catch (err) {
      console.error('生成失败:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  const toggleChar = (id: string) => {
    setSelectedChars(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  return (
    <div className="flex h-full">
      {/* 左侧生成面板 */}
      <aside className="w-80 border-r bg-white p-6 overflow-y-auto flex-shrink-0">
        <h2 className="text-xl font-bold mb-4">AI 插图生成</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">描述 Prompt</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="描述角色外貌或场景..."
              rows={4}
              className="w-full border rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">风格</label>
            <div className="flex flex-wrap gap-2">
              {STYLES.map(s => (
                <button
                  key={s.value}
                  onClick={() => setStyle(s.value)}
                  className={`px-3 py-1.5 text-sm rounded-lg border ${
                    style === s.value ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">尺寸</label>
            <select
              value={size}
              onChange={e => setSize(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
            >
              {SIZES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">关联角色</label>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {(characters || []).map(c => (
                <label key={c.id} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedChars.includes(c.id)}
                    onChange={() => toggleChar(c.id)}
                    className="rounded"
                  />
                  {c.name}
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isGenerating ? '生成中...' : '✨ 生成图片'}
          </button>
        </div>
      </aside>

      {/* 右侧画廊 */}
      <main className="flex-1 p-6 overflow-y-auto">
        {preview && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2">预览</h3>
            <img src={preview} alt="preview" className="max-w-md rounded-lg shadow-lg" />
          </div>
        )}

        <h3 className="font-semibold mb-3">生成历史</h3>
        {images.length === 0 ? (
          <p className="text-gray-400">暂无生成记录</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {images.map((img, i) => (
              <div key={i} className="border rounded-lg overflow-hidden cursor-pointer hover:shadow-md" onClick={() => setPreview(img.url)}>
                <img src={img.url} alt={img.prompt} className="w-full object-cover" />
                <div className="p-2">
                  <p className="text-xs text-gray-500 truncate">{img.prompt}</p>
                  {img.char && <p className="text-xs text-purple-500">{img.char}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
