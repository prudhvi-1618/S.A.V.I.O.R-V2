import type { ExtractedElement } from '../../extraction/types/extraction.types';
import type { BoundingBox, OverlayElement } from '../types/pdf.types';

export function transformCoordinates(
  points: number[][],
  pdfWidth: number,
  pdfHeight: number,
  renderedWidth: number,
  renderedHeight: number
): BoundingBox {
  const scaleX = renderedWidth / pdfWidth;
  const scaleY = renderedHeight / pdfHeight;

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const [x, y] of points) {
    const canvasX = x * scaleX;
    // Y-axis flip
    const canvasY = renderedHeight - (y * scaleY);
    
    minX = Math.min(minX, canvasX);
    minY = Math.min(minY, canvasY);
    maxX = Math.max(maxX, canvasX);
    maxY = Math.max(maxY, canvasY);
  }

  return {
    left: minX,
    top: minY,
    width: maxX - minX,
    height: maxY - minY
  };
}

export function hasValidCoordinates(element: ExtractedElement): boolean {
  return !!(
    element.coordinates &&
    element.coordinates.points &&
    element.coordinates.points.length === 4
  );
}

export function elementsForPage(
  elements: ExtractedElement[],
  pageNumber: number
): ExtractedElement[] {
  return elements.filter(el => el.page_number === pageNumber);
}

export function buildOverlayElements(
  elements: ExtractedElement[],
  pageNumber: number,
  renderedWidth: number,
  renderedHeight: number
): OverlayElement[] {
  const pageElements = elementsForPage(elements, pageNumber);
  const overlayElements: OverlayElement[] = [];

  for (const el of pageElements) {
    if (hasValidCoordinates(el) && el.coordinates) {
      const bbox = transformCoordinates(
        el.coordinates.points,
        el.coordinates.page_width,
        el.coordinates.page_height,
        renderedWidth,
        renderedHeight
      );

      overlayElements.push({
        element_id: el.element_id,
        element_type: el.element_type,
        text: el.text,
        page_number: el.page_number,
        bounding_box: bbox,
        has_image: !!el.metadata?.image_path,
        metadata: el.metadata
      });
    }
  }

  return overlayElements;
}
