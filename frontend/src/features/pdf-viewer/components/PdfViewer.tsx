import React, { useState, useRef, useEffect } from 'react';
import { Document, pdfjs } from 'react-pdf';
import type { ExtractedElement } from '../../extraction/types/extraction.types';
import type { OverlayElement, PageDimensions } from '../types/pdf.types';
import { PdfToolbar } from './PdfToolbar';
import { PdfPage } from './PdfPage';
import { usePdfNavigation } from '../hooks/usePdfNavigation';
import { buildOverlayElements } from '../utils/coordinates';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PdfViewerProps {
  fileUrl: string;
  elements: ExtractedElement[];
  selectedElementId: string | null;
  onElementClick: (element: OverlayElement) => void;
  hoveredElementId: string | null;
  onElementHover: (id: string | null) => void;
  currentPageProp?: number;
  onPageChange?: (page: number) => void;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({
  fileUrl,
  elements,
  selectedElementId,
  onElementClick,
  hoveredElementId,
  onElementHover,
  currentPageProp,
  onPageChange
}) => {
  const {
    currentPage,
    totalPages,
    scale,
    goToPage,
    setScale,
    setTotalPages
  } = usePdfNavigation(1.0);

  const containerRef = useRef<HTMLDivElement>(null);
  const [renderedDimensions, setRenderedDimensions] = useState<PageDimensions | null>(null);

  useEffect(() => {
    if (currentPageProp && currentPageProp !== currentPage) {
      goToPage(currentPageProp);
    }
  }, [currentPageProp, currentPage, goToPage]);

  // Scroll to selected element when it changes
  useEffect(() => {
    if (selectedElementId && renderedDimensions && containerRef.current) {
      // Re-calculate the selected element's overlay box based on the current page dimensions
      const overlayElements = buildOverlayElements(elements, currentPage, renderedDimensions.width, renderedDimensions.height);
      const selectedOverlay = overlayElements.find(el => el.element_id === selectedElementId);
      
      if (selectedOverlay) {
        const yOffset = selectedOverlay.bounding_box.top;
        // Smooth scroll the container
        containerRef.current.scrollTo({
          top: Math.max(0, yOffset - 50), // 50px padding above
          behavior: 'smooth'
        });
      }
    }
  }, [selectedElementId, renderedDimensions, elements, currentPage]);

  const handlePageChange = (newPage: number) => {
    goToPage(newPage);
    if (onPageChange) onPageChange(newPage);
  };

  const handlePageRender = (dimensions: PageDimensions) => {
    setRenderedDimensions(dimensions);
  };

  return (
    <div className="flex flex-col h-full bg-gray-100 rounded-lg overflow-hidden border">
      <Document
        file={fileUrl}
        onLoadSuccess={({ numPages }) => setTotalPages(numPages)}
        className="flex flex-col h-full"
        loading={<div className="p-8 text-center text-gray-500">Loading PDF...</div>}
        error={<div className="p-8 text-center text-red-500">Failed to load PDF. Check backend serving.</div>}
      >
        <PdfToolbar
          currentPage={currentPage}
          totalPages={totalPages}
          scale={scale}
          onPrev={() => handlePageChange(currentPage > 1 ? currentPage - 1 : currentPage)}
          onNext={() => handlePageChange(currentPage < totalPages ? currentPage + 1 : currentPage)}
          onScaleChange={setScale}
        />

        <div 
          ref={containerRef}
          className="flex-1 overflow-auto bg-gray-200 p-4 text-center flex justify-center scroll-smooth"
        >
          <PdfPage
            pageNumber={currentPage}
            scale={scale}
            elements={elements}
            selectedElementId={selectedElementId}
            hoveredElementId={hoveredElementId}
            onElementClick={onElementClick}
            onElementHover={onElementHover}
            onPageRender={handlePageRender}
          />
        </div>
      </Document>
    </div>
  );
};
