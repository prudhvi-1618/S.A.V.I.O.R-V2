import React from 'react';
import type { ExtractedElement } from '../../extraction/types/extraction.types';
import type { OverlayElement } from '../types/pdf.types';
import { ElementHighlight } from './ElementHighlight';
import { buildOverlayElements } from '../utils/coordinates';

interface PdfOverlayProps {
  elements: ExtractedElement[];
  pageNumber: number;
  renderedWidth: number;
  renderedHeight: number;
  selectedElementId: string | null;
  hoveredElementId: string | null;
  onElementClick: (element: OverlayElement) => void;
  onElementHover: (id: string | null) => void;
}

export const PdfOverlay: React.FC<PdfOverlayProps> = ({
  elements,
  pageNumber,
  renderedWidth,
  renderedHeight,
  selectedElementId,
  hoveredElementId,
  onElementClick,
  onElementHover
}) => {
  const overlayElements = buildOverlayElements(elements, pageNumber, renderedWidth, renderedHeight);

  if (renderedWidth === 0 || renderedHeight === 0) return null;

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: renderedWidth,
        height: renderedHeight,
        pointerEvents: "none"
      }}
    >
      {overlayElements.map(el => (
        <ElementHighlight
          key={el.element_id}
          element={el}
          isSelected={el.element_id === selectedElementId}
          isHovered={el.element_id === hoveredElementId}
          onClick={onElementClick}
          onHover={onElementHover}
        />
      ))}
    </svg>
  );
};
