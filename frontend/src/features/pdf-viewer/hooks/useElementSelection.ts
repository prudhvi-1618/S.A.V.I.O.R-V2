import { useState, useCallback } from 'react';
import type { OverlayElement } from '../types/pdf.types';

export interface UseElementSelectionReturn {
  selectedElement: OverlayElement | null;
  selectElement: (element: OverlayElement) => void;
  clearSelection: () => void;
  hoveredElementId: string | null;
  setHoveredElementId: (id: string | null) => void;
}

export const useElementSelection = (): UseElementSelectionReturn => {
  const [selectedElement, setSelectedElement] = useState<OverlayElement | null>(null);
  const [hoveredElementId, setHoveredElementId] = useState<string | null>(null);

  const selectElement = useCallback((element: OverlayElement) => {
    setSelectedElement(element);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedElement(null);
  }, []);

  return {
    selectedElement,
    selectElement,
    clearSelection,
    hoveredElementId,
    setHoveredElementId
  };
};
