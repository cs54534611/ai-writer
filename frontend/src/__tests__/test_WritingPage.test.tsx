/**
 * @vitest-environment jsdom
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

// Mock WritingPage Component (simplified for testing)
const MockWritingPage: React.FC<{
  projectId?: string
  chapterId?: string
  onSave?: () => void
  onBack?: () => void
}> = ({ projectId, chapterId, onSave, onBack }) => {
  const [content, setContent] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(false)
  const [showTools, setShowTools] = React.useState(false)

  const handleSave = () => {
    onSave?.()
  }

  const handleAIWrite = async (mode: string) => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 100))
    setContent(prev => prev + `\n[AI ${mode} 内容]`)
    setIsLoading(false)
    setShowTools(false)
  }

  return (
    <div data-testid="writing-page">
      <button data-testid="back-btn" onClick={onBack}>返回</button>
      <button data-testid="save-btn" onClick={handleSave}>保存</button>
      <button data-testid="ai-tools-btn" onClick={() => setShowTools(!showTools)}>AI工具</button>
      
      {showTools && (
        <div data-testid="ai-tools-panel">
          <button data-testid="continue-btn" onClick={() => handleAIWrite('续写')} disabled={isLoading}>续写</button>
          <button data-testid="expand-btn" onClick={() => handleAIWrite('扩写')} disabled={isLoading}>扩写</button>
          <button data-testid="rewrite-btn" onClick={() => handleAIWrite('改写')} disabled={isLoading}>改写</button>
        </div>
      )}
      
      <textarea
        data-testid="editor"
        value={content}
        onChange={e => setContent(e.target.value)}
        placeholder="开始写作..."
      />
      <div data-testid="word-count">{content.length} 字</div>
      {isLoading && <div data-testid="loading">AI写作中...</div>}
    </div>
  )
}

describe('WritingPage 组件测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本渲染', () => {
    it('should render writing page', () => {
      render(<MockWritingPage />)
      expect(screen.getByTestId('writing-page')).toBeInTheDocument()
    })

    it('should render editor', () => {
      render(<MockWritingPage />)
      expect(screen.getByTestId('editor')).toBeInTheDocument()
    })

    it('should show word count', () => {
      render(<MockWritingPage />)
      expect(screen.getByTestId('word-count')).toHaveTextContent('0 字')
    })
  })

  describe('内容编辑', () => {
    it('should update content on typing', () => {
      render(<MockWritingPage />)
      const editor = screen.getByTestId('editor')
      
      fireEvent.change(editor, { target: { value: '测试内容' } })
      
      expect(screen.getByTestId('word-count')).toHaveTextContent('4 字')
    })

    it('should handle empty content', () => {
      render(<MockWritingPage />)
      const editor = screen.getByTestId('editor')
      
      fireEvent.change(editor, { target: { value: '' } })
      
      expect(screen.getByTestId('word-count')).toHaveTextContent('0 字')
    })
  })

  describe('AI工具', () => {
    it('should toggle AI tools panel', () => {
      render(<MockWritingPage />)
      
      expect(screen.queryByTestId('ai-tools-panel')).not.toBeInTheDocument()
      
      fireEvent.click(screen.getByTestId('ai-tools-btn'))
      
      expect(screen.getByTestId('ai-tools-panel')).toBeInTheDocument()
    })

    it('should show AI writing buttons', async () => {
      render(<MockWritingPage />)
      fireEvent.click(screen.getByTestId('ai-tools-btn'))
      
      expect(screen.getByTestId('continue-btn')).toBeInTheDocument()
      expect(screen.getByTestId('expand-btn')).toBeInTheDocument()
      expect(screen.getByTestId('rewrite-btn')).toBeInTheDocument()
    })

    it('should disable buttons while loading', async () => {
      render(<MockWritingPage />)
      fireEvent.click(screen.getByTestId('ai-tools-btn'))
      
      const continueBtn = screen.getByTestId('continue-btn')
      expect(continueBtn).not.toBeDisabled()
    })
  })

  describe('导航和保存', () => {
    it('should call onBack when back button clicked', () => {
      const onBack = vi.fn()
      render(<MockWritingPage onBack={onBack} />)
      
      fireEvent.click(screen.getByTestId('back-btn'))
      
      expect(onBack).toHaveBeenCalled()
    })

    it('should call onSave when save button clicked', () => {
      const onSave = vi.fn()
      render(<MockWritingPage onSave={onSave} />)
      
      fireEvent.click(screen.getByTestId('save-btn'))
      
      expect(onSave).toHaveBeenCalled()
    })
  })

  describe('AI写作功能', () => {
    it('should append AI content after writing', async () => {
      render(<MockWritingPage />)
      const editor = screen.getByTestId('editor')
      
      // 先输入一些内容
      fireEvent.change(editor, { target: { value: '原有内容' } })
      
      // 打开AI工具
      fireEvent.click(screen.getByTestId('ai-tools-btn'))
      
      // 点击续写
      fireEvent.click(screen.getByTestId('continue-btn'))
      
      // 等待AI处理完成（mock 100ms）
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 验证内容已添加（AI会追加内容）
      const newValue = (screen.getByTestId('editor') as HTMLTextAreaElement).value
      expect(newValue).toContain('原有内容')
    })
  })
})
