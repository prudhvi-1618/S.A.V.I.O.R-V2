import { Routes, Route } from 'react-router-dom'
import { DocumentPage } from './pages/DocumentPage/DocumentPage'
import { HomePage } from './pages/HomePage/HomePage'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/document/:documentId" element={<DocumentPage />} />
      </Routes>
    </div>
  )
}

export default App
