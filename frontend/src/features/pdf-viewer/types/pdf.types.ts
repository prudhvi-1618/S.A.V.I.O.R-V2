import type { ExtractedElement } from '../../extraction/types/extraction.types';

export interface PageDimensions {
  width: number;
  height: number;
  pageNumber: number;
}

export interface BoundingBox {
  left: number;
  top: number;
  width: number;
  height: number;
}

export interface OverlayElement {
  element_id: string;
  element_type: string;
  text: string | null;
  page_number: number;
  bounding_box: BoundingBox;
  has_image: boolean;
  metadata?: Record<string, any>;
}

export interface PdfViewerState {
  currentPage: number;
  totalPages: number;
  scale: number;
  pageDimensions: Record<number, PageDimensions>;
}
