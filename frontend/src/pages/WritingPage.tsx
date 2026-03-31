import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useChapter, useCreateChapter, useUpdateChapter, useAIContinue } from '../hooks/useChapters'
import OutlineTree from '../components/OutlineTree'
import AIFeedbackPanel from '../components/AIFeedbackPanel'
import AIWritingPanel from '../components/AIWritingPanel'

export default function WritingPage() {
  const { projectId, chapterId } = useParams()
  const navigate = useNavigate()
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const [showOutline, setShowOutline] = useState(true)
  const [showAIPanel, setShowAIPanel] = useState(false)
  const [feedbackResult, setFeedbackResult] = useState<any>(null)
  const [wordCount, setWordCount] = useState(0)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [isTypingMode, setIsTypingMode] = useState(true)
  const [content, setContent] = useState('')
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const { data: chapter, isLoading } = useChapter(projectId!, chapterId!)
  const updateChapter = useUpdateChapter()
  const aiContinue = useAIContinue()

  // 同步章节内容到本地状态
  useEffect(() => {
    if (chapter?.content !== undefined) {
      setContent(chapter.content)
      const count = chapter.content.replace(/\s/g, '').length
      setWordCount(count)
    }
  }, [chapter?.content])

  // 打字机效果：当前行居中
  const scrollToCurrentLine = useCallback(() => {
    if (!isTypingMode || !textareaRef.current) return
    const textarea = textareaRef.current
    const lineHeight = 28
    const cursorPosition = textarea.selectionStart
    const textBeforeCursor = textarea.value.substring(0, cursorPosition)
    const lines = textBeforeCursor.split('\n').length
    const scrollTop = (lines - 1) * lineHeight - textarea.clientHeight / 2 + lineHeight
    textarea.scrollTop = Math.max(0, scrollTop)
  }, [isTypingMode])

  // 自动保存（30秒无操作后）
  useEffect(() => {
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    }
  }, [])

  const handleSave = async (contentToSave?: string) => {
    if (!chapter) return
    const contentToUse = contentToSave ?? content
    try {
      await updateChapter.mutateAsync({
        id: chapter.id,
        projectId: projectId!,
        data: { content: contentToUse, status: 'writing' }
      })
      setLastSaved(new Date())
    } catch (err) {
      console.error('保存失败:', err)
    }
  }

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    setContent(newContent)
    // 实时更新字数
    const count = newContent.replace(/\s/g, '').length
    setWordCount(count)
    // 触发自动保存计时器重置
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(() => {
      handleSave(newContent)
    }, 30000)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+S 保存
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      handleSave()
    }
    // Tab 缩进
    if (e.key === 'Tab') {
      e.preventDefault()
      const textarea = textareaRef.current
      if (!textarea) return
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const newContent = content.substring(0, start) + '    ' + content.substring(end)
      setContent(newContent)
      // 设置光标位置到插入后
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4
      })
    }
  }

  const handleAIContinue = async () => {
    if (!chapter) return
    try {
      const result = await aiContinue.mutateAsync({
        projectId: projectId!,
        chapterId: chapter.id,
        context: chapter.content,
        numVersions: 2
      })
      // 显示多版本候选浮层
      setShowAIPanel(true)
    } catch (err) {
      console.error('AI 续写失败:', err)
    }
  }

  const handleAIFeedback = async () => {
    if (!chapter) return
    try {
      const result = await fetch(`/api/v1/projects/${projectId}/writing/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: chapter.content })
      })
      const data = await result.json()
      setFeedbackResult(data)
    } catch (err) {
      console.error('AI 反馈失败:', err)
    }
  }

  // 插入 Markdown 格式化符号
  const insertFormat = (format: 'bold' | 'italic' | 'quote' | 'paragraph') => {
    const textarea = textareaRef.current
    if (!textarea) return
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = content.substring(start, end)
    
    let insertion = ''
    let cursorOffset = 0
    
    switch (format) {
      case 'bold':
        insertion = `**${selectedText || '粗体文字'}**`
        cursorOffset = selectedText ? insertion.length : 2
        break
      case 'italic':
        insertion = `*${selectedText || '斜体文字'}*`
        cursorOffset = selectedText ? insertion.length : 1
        break
      case 'quote':
        insertion = `\n> ${selectedText || '引用内容'}\n`
        cursorOffset = insertion.length
        break
      case 'paragraph':
        insertion = `\n---\n`
        cursorOffset = insertion.length
        break
    }
    
    const newContent = content.substring(0, start) + insertion + content.substring(end)
    setContent(newContent)
    requestAnimationFrame(() => {
      textarea.focus()
      textarea.selectionStart = textarea.selectionEnd = start + cursorOffset
    })
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">加载中...</div>
  }

  return (
    <div className="flex h-full bg-gray-50">
      {/* 左侧大纲树 */}
      {showOutline && (
        <aside className="w-64 border-r bg-white overflow-y-auto flex-shrink-0">
          <div className="p-3 border-b flex items-center justify-between">
            <span className="font-medium text-sm">章节目录</span>
            <button onClick={() => setShowOutline(false)} className="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <OutlineTree projectId={projectId!} currentChapterId={chapterId} />
        </aside>
      )}

      {/* 中间编辑器 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 工具栏 */}
        <div className="h-12 border-b bg-white flex items-center px-4 gap-2">
          {!showOutline && (
            <button onClick={() => setShowOutline(true)} className="text-sm text-gray-600 hover:text-blue-600">
              ☰ 目录
            </button>
          )}
          {/* 格式化工具栏 */}
          <div className="flex items-center gap-1 border-r pr-2">
            <button onClick={() => insertFormat('bold')} className="text-xs px-2 py-1 rounded hover:bg-gray-100" title="粗体 **">
              <strong>B</strong>
            </button>
            <button onClick={() => insertFormat('italic')} className="text-xs px-2 py-1 rounded hover:bg-gray-100" title="斜体 *">
              <em>I</em>
            </button>
            <button onClick={() => insertFormat('quote')} className="text-xs px-2 py-1 rounded hover:bg-gray-100" title="引用 >">
              "
            </button>
            <button onClick={() => insertFormat('paragraph')} className="text-xs px-2 py-1 rounded hover:bg-gray-100" title="分段 ---">
              —
            </button>
          </div>
          <div className="flex-1" />
          <span className="text-xs text-gray-400">
            {lastSaved ? `已保存 ${lastSaved.toLocaleTimeString('zh-CN')}` : '未保存'}
          </span>
          <button
            onClick={() => setIsTypingMode(!isTypingMode)}
            className={`text-xs px-2 py-1 rounded ${isTypingMode ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
          >
            打字机
          </button>
          <button
            onClick={() => setShowAIPanel(!showAIPanel)}
            className="text-xs px-3 py-1 bg-purple-100 text-purple-600 rounded hover:bg-purple-200"
          >
            ✨ AI 写作
          </button>
        </div>

        {/* 写作区域 */}
        <div className="flex-1 overflow-hidden p-8">
          <div className="max-w-3xl mx-auto h-full">
            {chapterId ? (
              <textarea
                ref={textareaRef}
                value={content}
                onChange={handleContentChange}
                onKeyUp={scrollToCurrentLine}
                onClick={scrollToCurrentLine}
                onKeyDown={handleKeyDown}
                className="w-full h-full resize-none border-0 bg-transparent outline-none text-gray-800 leading-relaxed"
                style={{ lineHeight: '1.8', fontSize: '16px' }}
                placeholder="开始你的创作..."
              />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <p className="mb-4">请从左侧目录选择一个章节</p>
                <button
                  onClick={() => navigate(`/projects/${projectId}/writing/new`)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  新建章节
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 底部状态栏 */}
        <div className="h-8 border-t bg-white flex items-center px-4 text-xs text-gray-400">
          <span>第 {chapter?.sort_order || 1} 章</span>
          <span className="mx-4">|</span>
          <span>{wordCount.toLocaleString()} 字</span>
          {chapter?.content && (
            <>
              <span className="mx-4">|</span>
              <span>写作进度 {Math.round(wordCount / 10000 * 100)}%</span>
            </>
          )}
        </div>
      </main>

      {/* 右侧 AI 面板 */}
      {showAIPanel && (
        <aside className="w-80 border-l bg-white overflow-y-auto flex-shrink-0">
          <div className="p-3 border-b flex items-center justify-between">
            <span className="font-medium text-sm">AI 写作助手</span>
            <button onClick={() => setShowAIPanel(false)} className="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <AIWritingPanel
            chapter={chapter}
            projectId={projectId}
            onInsertText={(text) => {
              setContent(prev => prev + '\n' + text)
            }}
            onFeedback={handleAIFeedback}
          />
          {feedbackResult && (
            <AIFeedbackPanel feedback={feedbackResult} />
          )}
        </aside>
      )}
    </div>
  )
}
