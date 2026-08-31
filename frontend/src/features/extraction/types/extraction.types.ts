export type ExtractionStatus = "idle" | "connecting" | "processing" | "completed" | "error";

export interface ElementCoordinates {
  points: number[][];
  page_width: number;
  page_height: number;
}

export interface ExtractedElement {
  element_id: string;
  document_id: string;
  element_type: string;
  text: string | null;
  page_number: number;
  coordinates?: ElementCoordinates;
  metadata?: Record<string, any>;
}

export interface ChunkData {
  chunk_id: string;
  chunk_text: string;
  chunk_type: string;
  embedded: boolean;
  image_description?: string;
}

export interface ExtractionEvent {
  event: string;
  data: any;
}

export interface ProcessingStep {
  id: string;
  label: string;
  status: "pending" | "active" | "completed";
}
