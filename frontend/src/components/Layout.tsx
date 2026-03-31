import { ReactNode, useState, useEffect, useCallback } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useVoiceInput } from '../hooks/useVoiceInput'

interface LayoutProps {
  children: ReactNode
}

interface VoiceInputLayerProps {
  onClose: () => void
  onCopy: (text: string) => void
  onSendToInspiration: (text: string) => void
}

function VoiceInputLayer({ onClose, onCopy, onSendToInspiration }: VoiceInputLayerProps) {
  const [fullTranscript, setFullTranscript] = useState('')
  
  const handleResult = useCallback((text: string) => {
    setFullTranscript(prev => prev + text)
  }, [])
  
  const {
    isListening,
    transcript,
    interimTranscript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported,
  } = useVoiceInput({ onResult: handleResult })

  const handleCopy = () => {
    if (fullTranscript) {
      onCopy(fullTranscript)
    }
  }

  const handleSendToInspiration = () => {
    if (fullTranscript) {
      onSendToInspiration(fullTranscript)
      resetTranscript()
      onClose()
    }
  }

  const handleToggle = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">语音输入</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {!isSupported ? (
          <div className="text-center py-8 text-gray-500">
            <p>当前浏览器不支持语音识别</p>
            <p className="text-sm mt-2">请使用 Chrome、Edge 或 Safari 浏览器</p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <div 
                className={`p-4 border-2 rounded-lg min-h-32 ${
                  isListening ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="text-gray-700 whitespace-pre-wrap">
                  {fullTranscript}
                  {interimTranscript && (
                    <span className="text-gray-400">{interimTranscript}</span>
                  )}
                  {!fullTranscript && !interimTranscript && (
                    <span className="text-gray-400">
                      {isListening ? '正在聆听...' : '点击开始按钮开始语音输入'}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-center gap-4 mb-4">
              <button
                onClick={handleToggle}
                className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl transition-all ${
                  isListening 
                    ? 'bg-red-500 text-white animate-pulse' 
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {isListening ? '⏹' : '🎤'}
              </button>
            </div>
            
            <div className="text-center text-sm text-gray-500 mb-4">
              {isListening ? '正在聆听中...' : '点击麦克风开始录音'}
            </div>
            
            {fullTranscript && (
              <div className="flex gap-2">
                <button
                  onClick={handleCopy}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  📋 复制
                </button>
                <button
                  onClick={handleSendToInspiration}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  💡 发送到灵感速记
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [showVoiceInput, setShowVoiceInput] = useState(false)

  const navItems = [
    { path: '/projects', label: '项目列表' },
  ]

  // Ctrl+Shift+N 全局快捷键监听
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 检查 Ctrl+Shift+N
      if (e.ctrlKey && e.shiftKey && e.key === 'N') {
        e.preventDefault()
        setShowVoiceInput(prev => !prev)
      }
      // ESC 关闭语音输入
      if (e.key === 'Escape' && showVoiceInput) {
        setShowVoiceInput(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [showVoiceInput])

  const handleCopyVoiceText = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('已复制到剪贴板')
    })
  }

  const handleSendToInspiration = (text: string) => {
    // 这里可以调用灵感速记的 API
    console.log('发送到灵感速记:', text)
    alert('已发送到灵感速记')
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold">AI Writer</h1>
          <p className="text-xs text-gray-500 mt-1">按 Ctrl+Shift+N 语音输入</p>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`block px-4 py-2 rounded-lg transition-colors ${
                    location.pathname.startsWith(item.path)
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="p-4 border-t border-gray-800 text-sm text-gray-500">
          AI Writer v0.1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50">
        {children}
      </main>

      {/* Voice Input Layer */}
      {showVoiceInput && (
        <VoiceInputLayer
          onClose={() => setShowVoiceInput(false)}
          onCopy={handleCopyVoiceText}
          onSendToInspiration={handleSendToInspiration}
        />
      )}
    </div>
  )
}
