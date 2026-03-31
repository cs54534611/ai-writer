import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useCharacters } from '../hooks/useCharacters'

interface Message {
  id: string
  role: 'user' | 'ai' | 'system'
  content: string
  character?: string
}

export default function DialogueWritingPage() {
  const { projectId } = useParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [scene, setScene] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { data: characters } = useCharacters(projectId!)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(`/api/v1/projects/${projectId}/chapters/dialogue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          characters: characters || [],
          scene,
          last_dialogue: input,
          history: messages.slice(-10)
        })
      })
      const data = await res.json()
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: data.dialogue || data.response || '（无内容）'
      }
      setMessages(prev => [...prev, aiMsg])
    } catch (err) {
      console.error('对话失败:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full bg-gray-50">
      {/* 左侧角色列表 */}
      <aside className="w-56 border-r bg-white overflow-y-auto">
        <div className="p-3 border-b font-medium text-sm">当前角色</div>
        {(characters || []).map((char: any) => (
          <div key={char.id} className="p-3 border-b hover:bg-gray-50 cursor-pointer">
            <p className="font-medium text-sm">{char.name}</p>
            <p className="text-xs text-gray-500">{char.personality?.substring(0, 20)}...</p>
          </div>
        ))}
        {(!characters || characters.length === 0) && (
          <p className="p-4 text-sm text-gray-400">暂无角色</p>
        )}
      </aside>

      {/* 中间对话区 */}
      <div className="flex-1 flex flex-col">
        {/* 场景描述 */}
        <div className="p-3 border-b bg-blue-50">
          <textarea
            value={scene}
            onChange={e => setScene(e.target.value)}
            placeholder="描述当前场景..."
            className="w-full text-sm bg-transparent resize-none outline-none"
            rows={2}
          />
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-16">
              <p>开始对话式写作</p>
              <p className="text-xs mt-1">选择一个角色，以对话形式推进剧情</p>
            </div>
          )}
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-md px-4 py-2 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'system'
                    ? 'bg-gray-200 text-gray-700'
                    : 'bg-white border shadow-sm'
                }`}
              >
                {msg.role === 'ai' && (
                  <p className="text-xs text-purple-600 mb-1">AI · {msg.character || '角色'}</p>
                )}
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border shadow-sm px-4 py-2 rounded-lg">
                <span className="text-sm text-gray-400 animate-pulse">AI 思考中...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <div className="p-4 border-t bg-white">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入对话..."
              className="flex-1 border rounded-lg px-3 py-2 text-sm resize-none outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 self-end"
            >
              发送
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-1">Enter 发送，Shift+Enter 换行</p>
        </div>
      </div>
    </div>
  )
}
