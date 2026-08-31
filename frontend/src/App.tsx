import React from 'react'
import { DocumentPage } from './pages/DocumentPage/DocumentPage'
import { HomePage } from './pages/HomePage/HomePage'
import { useDocumentStore } from './store/document.store'
import './App.css'

function App() {
  const { activeDocumentId, setActiveDocumentId } = useDocumentStore();

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {activeDocumentId ? (
        <DocumentPage documentId={activeDocumentId} />
      ) : (
        <HomePage onUploadSuccess={setActiveDocumentId} />
      )}
    </div>
  )
}

export default App
