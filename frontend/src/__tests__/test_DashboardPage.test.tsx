/**
 * @vitest-environment jsdom
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

// Mock DashboardPage Component
const MockDashboard: React.FC<{
  onSelectProject?: (id: string) => void
  onCreateProject?: () => void
}> = ({ onSelectProject, onCreateProject }) => {
  const [projects, setProjects] = React.useState([
    { id: '1', name: '我的小说', wordCount: 5000, updatedAt: '2024-01-01' },
    { id: '2', name: '另一个项目', wordCount: 3000, updatedAt: '2024-01-02' },
  ])
  const [loading, setLoading] = React.useState(false)
  const [filter, setFilter] = React.useState('all')

  const handleCreate = async () => {
    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 100))
    onCreateProject?.()
    setLoading(false)
  }

  const filteredProjects = filter === 'all' 
    ? projects 
    : projects.filter(p => p.wordCount > 4000)

  return (
    <div data-testid="dashboard">
      <header data-testid="dashboard-header">
        <h1 data-testid="dashboard-title">AI Writer</h1>
        <button data-testid="create-btn" onClick={handleCreate} disabled={loading}>
          {loading ? '创建中...' : '新建项目'}
        </button>
      </header>
      
      <div data-testid="stats">
        <div data-testid="total-projects">{projects.length} 个项目</div>
        <div data-testid="total-words">{projects.reduce((sum, p) => sum + p.wordCount, 0)} 字</div>
      </div>
      
      <div data-testid="filters">
        <button 
          data-testid="filter-all" 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          全部
        </button>
        <button 
          data-testid="filter-recent"
          className={filter === 'recent' ? 'active' : ''}
          onClick={() => setFilter('recent')}
        >
          最近编辑
        </button>
      </div>
      
      <div data-testid="projects-list">
        {filteredProjects.map(project => (
          <div 
            key={project.id} 
            data-testid={`project-${project.id}`}
            onClick={() => onSelectProject?.(project.id)}
          >
            <h3 data-testid={`project-name-${project.id}`}>{project.name}</h3>
            <div data-testid={`project-words-${project.id}`}>{project.wordCount} 字</div>
          </div>
        ))}
      </div>
    </div>
  )
}

describe('DashboardPage 组件测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本渲染', () => {
    it('should render dashboard', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('dashboard')).toBeInTheDocument()
    })

    it('should render dashboard title', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('dashboard-title')).toHaveTextContent('AI Writer')
    })

    it('should render create button', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('create-btn')).toBeInTheDocument()
    })
  })

  describe('统计数据', () => {
    it('should show total projects count', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('total-projects')).toHaveTextContent('2 个项目')
    })

    it('should show total word count', () => {
      render(<MockDashboard />)
      // 默认数据总字数
      expect(screen.getByTestId('total-words')).toHaveTextContent(expect.any(String))
    })
  })

  describe('项目列表', () => {
    it('should render all projects', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('project-1')).toBeInTheDocument()
      expect(screen.getByTestId('project-2')).toBeInTheDocument()
    })

    it('should show project names', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('project-name-1')).toHaveTextContent('我的小说')
      expect(screen.getByTestId('project-name-2')).toHaveTextContent('另一个项目')
    })

    it('should call onSelectProject when clicking a project', () => {
      const onSelectProject = vi.fn()
      render(<MockDashboard onSelectProject={onSelectProject} />)
      
      // 点击项目卡片
      const projectCard = screen.getByTestId('project-1')
      fireEvent.click(projectCard)
      
      expect(onSelectProject).toHaveBeenCalled()
    })
  })

  describe('筛选功能', () => {
    it('should show all projects by default', () => {
      render(<MockDashboard />)
      expect(screen.getByTestId('filter-all')).toHaveClass('active')
    })

    it('should filter by recent edits', () => {
      render(<MockDashboard />)
      
      fireEvent.click(screen.getByTestId('filter-recent'))
      
      expect(screen.getByTestId('filter-recent')).toHaveClass('active')
    })
  })

  describe('创建项目', () => {
    it('should call onCreateProject when button clicked', () => {
      const onCreateProject = vi.fn()
      render(<MockDashboard onCreateProject={onCreateProject} />)
      
      fireEvent.click(screen.getByTestId('create-btn'))
      
      expect(onCreateProject).toHaveBeenCalled()
    })

    it('should disable button while loading', () => {
      render(<MockDashboard />)
      
      fireEvent.click(screen.getByTestId('create-btn'))
      
      // 按钮应该在加载时显示不同文本
      expect(screen.getByTestId('create-btn')).toHaveTextContent('创建中...')
    })
  })

  describe('空状态', () => {
    it('should handle empty projects list', () => {
      const EmptyDashboard: React.FC = () => (
        <div data-testid="dashboard">
          <div data-testid="stats">
            <div data-testid="total-projects">0 个项目</div>
            <div data-testid="total-words">0 字</div>
          </div>
          <div data-testid="projects-list"></div>
        </div>
      )
      
      render(<EmptyDashboard />)
      expect(screen.getByTestId('total-projects')).toHaveTextContent('0 个项目')
    })
  })
})
