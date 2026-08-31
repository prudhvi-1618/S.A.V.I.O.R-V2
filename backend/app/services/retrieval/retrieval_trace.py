from dataclasses import dataclass
from typing import List

@dataclass
class TraceChunk:
    rank: int
    chunk_id: str
    similarity_score: float
    page_number: int
    chunk_type: str
    element_ids: List[str]
    element_types: List[str]
    content_preview: str

@dataclass
class RetrievalTrace:
    question: str
    retrieved_chunks: List[TraceChunk]
    total_results: int
    context_preview: str
