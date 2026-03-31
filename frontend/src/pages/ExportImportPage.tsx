import { useParams } from 'react-router-dom'
import { useExportImport } from '../hooks/useExportImport'
import ExportPanel from '../components/ExportPanel'
import ImportPanel from '../components/ImportPanel'

export default function ExportImportPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { loading, exportProject, importProject, importChaptersFromFolder } = useExportImport()

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
      </div>
    </div>
  )
}
