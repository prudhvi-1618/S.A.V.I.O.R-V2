import React, { useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useExtractionStream } from '../../features/extraction/hooks/useExtractionStream';
import { ExtractionPanel } from '../../features/extraction/components/ExtractionPanel';
import { ElementInspector } from '../../features/extraction/components/ElementInspector';
import { ChatInterface } from '../../features/chat/components/ChatInterface';
import { PdfViewer } from '../../features/pdf-viewer/components/PdfViewer';
import { useElementSelection } from '../../features/pdf-viewer/hooks/useElementSelection';
import type { OverlayElement } from '../../features/pdf-viewer/types/pdf.types';

export const DocumentPage: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();

  if (!documentId) {
    return <Navigate to="/" />;
  }

  const pdfUrl = `${import.meta.env.VITE_API_URL || ''}/api/v1/documents/${documentId}/file`;

  
  const { 
    status, 
    elements, 
    currentPage, 
    totalElements, 
    error,
    totalChunks,
    embeddedCount,
    processingImage 
  } = useExtractionStream(documentId, true);
  
  const { selectedElement, selectElement, clearSelection, hoveredElementId, setHoveredElementId } = useElementSelection();
  
  const [syncPage, setSyncPage] = useState<number | undefined>(undefined);

  const handleElementClick = (element: OverlayElement) => {
    selectElement(element);
    setSyncPage(element.page_number);
  };

  const handleSourceClick = (elementId: string, pageNumber: number) => {
    const el = elements.find(e => e.element_id === elementId);
    if (el) {
      selectElement(el as any);
      setSyncPage(pageNumber);
    } else {
      // Fallback if element not in list (e.g., truncated list)
      setSyncPage(pageNumber);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 p-4 space-x-4">
      {/* Left Panel: PDF Viewer */}
      <div className="flex-1 flex flex-col min-w-0">
        <PdfViewer
          fileUrl={pdfUrl}
          elements={elements}
          selectedElementId={selectedElement?.element_id || null}
          hoveredElementId={hoveredElementId}
          onElementClick={handleElementClick}
          onElementHover={setHoveredElementId}
          currentPageProp={syncPage}
          onPageChange={(page) => setSyncPage(page)}
        />
      </div>

      {/* Right Panel: Processing / Inspector */}
      <div className="w-[450px] flex flex-col shrink-0">
        {status !== 'completed' && status !== 'error' ? (
          <ExtractionPanel 
            status={status}
            elements={elements}
            currentPage={currentPage}
            totalElements={totalElements}
            error={error}
            totalChunks={totalChunks}
            embeddedCount={embeddedCount}
            processingImage={processingImage}
          />
        ) : selectedElement ? (
          <ElementInspector 
            element={selectedElement}
            onClose={clearSelection}
          />
        ) : (
          <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border overflow-hidden">
            <ChatInterface 
              documentId={documentId} 
              onSourceClick={handleSourceClick} 
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentPage;
