import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import CharactersPage from './pages/CharactersPage'
import RelationshipGraph from './pages/RelationshipGraph'
import InspirationsPage from './pages/InspirationsPage'
import WritingPage from './pages/WritingPage'
import DialogueWritingPage from './pages/DialogueWritingPage'
import ReviewPage from './pages/ReviewPage'
import ImageGalleryPage from './pages/ImageGalleryPage'
import FandomWorkflowPage from './pages/FandomWorkflowPage'
import DashboardPage from './pages/DashboardPage'
import PluginsPage from './pages/PluginsPage'
import ExportImportPage from './pages/ExportImportPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        <Route path="/projects/:projectId/characters" element={<CharactersPage />} />
        <Route path="/projects/:projectId/relationships" element={<RelationshipGraph />} />
        <Route path="/projects/:projectId/inspirations" element={<InspirationsPage />} />
        <Route path="/projects/:projectId/writing" element={<WritingPage />} />
        <Route path="/projects/:projectId/writing/chapters/:chapterId" element={<WritingPage />} />
        <Route path="/projects/:projectId/dialogue" element={<DialogueWritingPage />} />
        <Route path="/projects/:projectId/review" element={<ReviewPage />} />
        <Route path="/projects/:projectId/review/chapters/:chapterId" element={<ReviewPage />} />
        <Route path="/projects/:projectId/images" element={<ImageGalleryPage />} />
        <Route path="/projects/:projectId/fandom" element={<FandomWorkflowPage />} />
        <Route path="/projects/:projectId/dashboard" element={<DashboardPage />} />
        <Route path="/projects/:projectId/export-import" element={<ExportImportPage />} />
        <Route path="/plugins" element={<PluginsPage />} />
        <Route path="/" element={<Navigate to="/projects" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
