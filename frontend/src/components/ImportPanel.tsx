import { useState, useCallback, DragEvent } from 'react'
import { ExportFormat } from '../hooks/useExportImport'

interface ImportPanelProps {
  projectId: string
  onImport: (projectId: string, file: File, format: ExportFormat) => Promise<void>
  onImportFolder?: (projectId: string, folderPath: string) => Promise<void>
  loading?: boolean
}

type ConflictStrategy = 'skip' | 'overwrite' | 'create'

export default function ImportPanel({
  projectId,
  onImport,
  onImportFolder,
  loading = false,
}: ImportPanelProps) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importFormat, setImportFormat] = useState<ExportFormat>('json')
  const [conflictStrategy, setConflictStrategy] = useState<ConflictStrategy>('skip')
  const [importing, setImporting] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      setSelectedFile(file)
      // Auto-detect format from file extension
      if (file.name.endsWith('.json')) setImportFormat('json')
      else if (file.name.endsWith('.zip')) setImportFormat('zip')
      else if (file.name.endsWith('.md')) setImportFormat('markdown')
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
    }
  }

  const handleImport = async () => {
    if (!selectedFile) return
    setImporting(true)
    try {
      await onImport(projectId, selectedFile, importFormat)
      setSelectedFile(null)
      setPreviewData(null)
    } finally {
      setImporting(false)
    }
  }

  const getFileIcon = (file: File) => {
    if (file.name.endsWith('.json')) return '📄'
    if (file.name.endsWith('.zip')) return '📦'
    if (file.name.endsWith('.md')) return '📝'
    return '📁'
  }

  return (
    <div className="import-panel">
      <h3>导入数据</h3>

      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="drop-zone-content">
          <span className="drop-icon">📂</span>
          <p>拖拽文件到这里，或 <label className="btn-link">点击选择<input type="file" onChange={handleFileSelect} accept=".json,.zip,.md" /></label></p>
          <span className="drop-hint">支持 JSON、ZIP、Markdown 格式</span>
        </div>
      </div>

      {selectedFile && (
        <div className="selected-file">
          <span className="file-icon">{getFileIcon(selectedFile)}</span>
          <div className="file-info">
            <strong>{selectedFile.name}</strong>
            <span>{(selectedFile.size / 1024).toFixed(1)} KB</span>
          </div>
          <button
            type="button"
            className="btn-icon"
            onClick={() => setSelectedFile(null)}
          >
            ✕
          </button>
        </div>
      )}

      {selectedFile && (
        <>
          <div className="import-options">
            <label>
              <span>导入格式：</span>
              <select
                value={importFormat}
                onChange={(e) => setImportFormat(e.target.value as ExportFormat)}
              >
                <option value="json">JSON</option>
                <option value="markdown">Markdown</option>
                <option value="zip">ZIP</option>
              </select>
            </label>

            <label>
              <span>冲突处理：</span>
              <select
                value={conflictStrategy}
                onChange={(e) => setConflictStrategy(e.target.value as ConflictStrategy)}
              >
                <option value="skip">跳过已存在</option>
                <option value="overwrite">覆盖</option>
                <option value="create">新建副本</option>
              </select>
            </label>
          </div>

          <div className="import-preview">
            <h4>导入预览</h4>
            <div className="preview-content">
              <p>文件：{selectedFile.name}</p>
              <p>格式：{importFormat.toUpperCase()}</p>
              <p>策略：{conflictStrategy === 'skip' ? '跳过已存在' : conflictStrategy === 'overwrite' ? '覆盖' : '新建副本'}</p>
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={handleImport}
            disabled={importing || loading}
          >
            {importing ? '导入中...' : '确认导入'}
          </button>
        </>
      )}

      {onImportFolder && (
        <div className="folder-import-section">
          <h4>从文件夹导入章节</h4>
          <p className="hint">支持导入包含 Markdown 文件的文件夹</p>
          <button
            className="btn-secondary"
            onClick={() => {
              const path = prompt('请输入文件夹路径：')
              if (path) onImportFolder(projectId, path)
            }}
            disabled={loading}
          >
            选择文件夹
          </button>
        </div>
      )}
    </div>
  )
}
