export interface ChatSource {
  source_id: string;
  chunk_id: string;
  element_id: string;
  element_type: string;
  page_number: number;
  coordinates: Record<string, unknown>[] | null;
  similarity_score: number;
  preview: string;
  image_path: string | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
}
