import React, { useState } from 'react';
import { Page } from 'react-pdf';
import type { ExtractedElement } from '../../extraction/types/extraction.types';
import type { OverlayElement, PageDimensions } from '../types/pdf.types';
import { PdfOverlay } from './PdfOverlay';

import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

interface PdfPageProps {
  pageNumber: number;
  scale: number;
  elements: ExtractedElement[];
  selectedElementId: string | null;
  hoveredElementId: string | null;
  onElementClick: (element: OverlayElement) => void;
  onElementHover: (id: string | null) => void;
  onPageRender: (dimensions: PageDimensions) => void;
}

export const PdfPage: React.FC<PdfPageProps> = ({
  pageNumber,
  scale,
  elements,
  selectedElementId,
  hoveredElementId,
  onElementClick,
  onElementHover,
  onPageRender
}) => {
  const [renderedDimensions, setRenderedDimensions] = useState<{width: number, height: number} | null>(null);

  return (
    <div style={{ position: "relative", display: "inline-block", margin: "0 auto" }}>
      <Page
        pageNumber={pageNumber}
        scale={scale}
        onRenderSuccess={(page) => {
          const viewport = page.getViewport({ scale });
          const width = viewport.width;
          const height = viewport.height;
          setRenderedDimensions({ width, height });
          onPageRender({ width, height, pageNumber });
        }}
        renderTextLayer={false}
        renderAnnotationLayer={false}
        className="shadow-md bg-white"
      />
      
      {renderedDimensions && (
        <PdfOverlay
          elements={elements}
          pageNumber={pageNumber}
          renderedWidth={renderedDimensions.width}
          renderedHeight={renderedDimensions.height}
          selectedElementId={selectedElementId}
          hoveredElementId={hoveredElementId}
          onElementClick={onElementClick}
          onElementHover={onElementHover}
        />
      )}
    </div>
  );
};
