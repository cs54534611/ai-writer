import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useCharacters } from '../hooks/useCharacters'
import { useGenerateImage, useApplyImageToCharacter, type ImageGenerateParams } from '../hooks/useImageGen'

const STYLE_OPTIONS = [
  { value: 'anime', label: '动漫风', icon: '🎨' },
  { value: 'realistic', label: '写实风', icon: '📷' },
  { value: 'ink', label: '水墨风', icon: '🖌️' },
  { value: 'watercolor', label: '水彩风', icon: '🌸' },
]

interface ImageGeneratorProps {
  projectId: string
  onGenerated?: (image: any) => void
}

export default function ImageGenerator({ projectId, onGenerated }: ImageGeneratorProps) {
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState<ImageGenerateParams['style']>('anime')
  const [selectedCharacters, setSelectedCharacters] = useState<string[]>([])
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [generatedImageId, setGeneratedImageId] = useState<string | null>(null)

  const { data: characters } = useCharacters(projectId)
  const generateImage = useGenerateImage()
  const applyImage = useApplyImageToCharacter()

  const toggleCharacter = (characterId: string) => {
    setSelectedCharacters((prev) =>
      prev.includes(characterId)
        ? prev.filter((id) => id !== characterId)
        : [...prev, characterId]
    )
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    try {
      const result = await generateImage.mutateAsync({
        projectId,
        params: {
          prompt,
          style,
          character_ids: selectedCharacters.length > 0 ? selectedCharacters : undefined,
        },
      })

      if (result?.data?.image_data) {
        setPreviewImage(result.data.image_data)
        setGeneratedImageId(result.data.id)
        onGenerated?.(result.data)
      }
    } catch (err) {
      console.error('Failed to generate image:', err)
    }
  }

  const handleDownload = () => {
    if (!previewImage) return
    const link = document.createElement('a')
    link.href = previewImage
    link.download = `ai-writer-${Date.now()}.png`
    link.click()
  }

  const handleApplyToCharacter = async (characterId: string) => {
    if (!generatedImageId) return
    try {
      await applyImage.mutateAsync({ projectId, characterId, imageId: generatedImageId })
      alert('已成功应用到角色卡！')
    } catch (err) {
      console.error('Failed to apply image:', err)
    }
  }

  const isLoading = generateImage.isPending

  return (
    <div className="space-y-6">
      {/* Prompt Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          描述画面
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="描述你想要生成的画面，如：一位身着古装的少女站在樱花树下..."
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      {/* Style Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择风格
        </label>
        <div className="grid grid-cols-4 gap-2">
          {STYLE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setStyle(opt.value as ImageGenerateParams['style'])}
              className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                style === opt.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span className="text-2xl mb-1">{opt.icon}</span>
              <span className="text-xs font-medium">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Character Selection */}
      {characters && characters.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            关联角色（可选）
          </label>
          <div className="flex flex-wrap gap-2">
            {characters.map((char: any) => (
              <button
                key={char.id}
                onClick={() => toggleCharacter(char.id)}
                className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                  selectedCharacters.includes(char.id)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {char.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={!prompt.trim() || isLoading}
        className="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            生成中...
          </span>
        ) : (
          '✨ 生成插图'
        )}
      </button>

      {/* Preview Area */}
      {previewImage && (
        <div className="space-y-4">
          <div className="relative rounded-lg overflow-hidden border border-gray-200">
            <img src={previewImage} alt="Generated" className="w-full" />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              📥 下载图片
            </button>
            {selectedCharacters.length > 0 && (
              <div className="flex-1 relative">
                <select
                  onChange={(e) => handleApplyToCharacter(e.target.value)}
                  defaultValue=""
                  className="w-full py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors appearance-none"
                >
                  <option value="" disabled>应用到角色...</option>
                  {characters?.map((char: any) => (
                    <option key={char.id} value={char.id}>
                      {char.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
