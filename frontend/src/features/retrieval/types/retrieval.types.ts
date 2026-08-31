export interface RetrievalResult {
  rank: number;
  chunk_id: string;
  similarity_score: number;
  page_number: number;
  chunk_type: string;
  element_ids: string[];
  element_types: string[];
  content_preview: string;
}

export interface RetrievalTrace {
  question: string;
  total_results: number;
  retrieved_chunks: RetrievalResult[];
  context_preview: string;
  pipeline_counts?: {
    total_elements: number;
    total_chunks: number;
    vector_hits: number;
  };
}
