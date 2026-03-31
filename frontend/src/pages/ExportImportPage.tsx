import { useParams } from 'react-router-dom'
import { useExportImport, useExportPDF } from '../hooks/useExportImport'
import ExportPanel from '../components/ExportPanel'
import ImportPanel from '../components/ImportPanel'

export default function ExportImportPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { loading, exportProject, importProject, importChaptersFromFolder } = useExportImport()
  const { loading: pdfLoading, exportProjectPDF } = useExportPDF()

  if (!projectId) {
    return <div className="error-message">项目ID无效</div>
  }

  return (
    <div className="export-import-page">
      <header className="page-header">
        <h1>数据导入导出</h1>
      </header>

      <div className="panels-container">
        <div className="panel-wrapper">
          <ExportPanel
            projectId={projectId}
            onExport={exportProject}
            loading={loading}
          />
        </div>

        <div className="panel-wrapper">
          <ImportPanel
            projectId={projectId}
            onImport={importProject}
            onImportFolder={importChaptersFromFolder}
            loading={loading}
          />
        </div>

        {/* PDF导出面板 */}
        <div className="panel-wrapper">
          <div className="export-panel">
            <h3>导出为 PDF</h3>
            <p className="text-sm text-gray-600 mb-4">
              将项目导出为 PDF 电子书格式，包含封面、目录和所有章节内容。
            </p>
            <button
              className="btn-primary w-full"
              onClick={() => exportProjectPDF(projectId)}
              disabled={pdfLoading}
            >
              {pdfLoading ? '生成中...' : '下载 PDF 文件'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
