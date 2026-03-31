import { useState } from 'react'
import { ExportFormat } from '../hooks/useExportImport'

interface ExportPanelProps {
  projectId: string
  onExport: (projectId: string, format: ExportFormat) => Promise<void>
  loading?: boolean
}

const formatOptions: { value: ExportFormat; label: string; desc: string }[] = [
  { value: 'json', label: 'JSON', desc: '完整项目数据，包含所有设置' },
  { value: 'markdown', label: 'Markdown', desc: '章节内容导出为 Markdown 文件' },
  { value: 'zip', label: 'ZIP', desc: '包含所有资源的完整备份' },
]

const exportPreview = {
  json: ['项目设置', '角色数据', '关系图谱', '章节内容', '灵感素材', '写作历史'],
  markdown: ['所有章节内容', '角色介绍', '世界观设定'],
  zip: ['完整项目数据', '所有图片资源', '所有附件', '配置备份'],
}

export default function ExportPanel({ projectId, onExport, loading = false }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('json')
  const [exporting, setExporting] = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  const handleExport = async () => {
    setExporting(true)
    try {
      await onExport(projectId, selectedFormat)
    } finally {
      setExporting(false)
    }
  }

  const estimatedSize = {
    json: '~2.5 MB',
    markdown: '~1.8 MB',
    zip: '~15 MB',
  }

  return (
    <div className="export-panel">
      <h3>导出项目</h3>

      <div className="format-selector">
        <label>选择格式</label>
        <div className="format-options">
          {formatOptions.map((option) => (
            <label
              key={option.value}
              className={`format-option ${selectedFormat === option.value ? 'selected' : ''}`}
            >
              <input
                type="radio"
                name="exportFormat"
                value={option.value}
                checked={selectedFormat === option.value}
                onChange={() => setSelectedFormat(option.value)}
              />
              <span className="format-label">{option.label}</span>
              <span className="format-desc">{option.desc}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="export-estimate">
        <span>预估大小：</span>
        <strong>{estimatedSize[selectedFormat]}</strong>
      </div>

      <div className="export-preview-toggle">
        <button
          type="button"
          className="btn-link"
          onClick={() => setShowPreview(!showPreview)}
        >
          {showPreview ? '隐藏' : '显示'}导出预览
        </button>
      </div>

      {showPreview && (
        <div className="export-preview">
          <h4>将包含以下内容：</h4>
          <ul>
            {exportPreview[selectedFormat].map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        className="btn-primary"
        onClick={handleExport}
        disabled={exporting || loading}
      >
        {exporting ? '导出中...' : `下载 ${selectedFormat.toUpperCase()} 文件`}
      </button>
    </div>
  )
}
