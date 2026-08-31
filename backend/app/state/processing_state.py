from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from app.repositories.element_repository import ElementRepository

@dataclass
class ChunkData:
    chunk_id: str
    chunk_text: str
    chunk_index: int
    element_ids: List[str]
    element_types: List[str]
    page_numbers: List[int]
    primary_page: int
    chunk_type: str        # "text" | "image" | "table"
    image_path: Optional[str] = None
    image_description: Optional[str] = None
    coordinates: Optional[List[dict]] = None
    qdrant_id: Optional[str] = None
    embedded: bool = False

class ProcessingState:
    def __init__(self):
        self.chunks: List[ChunkData] = []
        self.embedding_status: str = "idle"  # "idle" | "processing" | "completed" | "failed"
        self.total_chunks: int = 0
        self.embedded_chunks: int = 0

    def add_chunk(self, chunk: ChunkData):
        self.chunks.append(chunk)
        self.total_chunks += 1

    def update_embedding_progress(self, embedded: int, total: int):
        self.embedded_chunks = embedded
        self.total_chunks = total

    def get_element_by_id(self, element_id: str) -> Optional[Any]:
        return ElementRepository.get(element_id)

    def get_all_elements(self) -> List[Any]:
        return ElementRepository.get_all()

    def get_chunk_by_element_id(self, element_id: str) -> Optional[ChunkData]:
        for chunk in self.chunks:
            if element_id in chunk.element_ids:
                return chunk
        return None

# Global instance for the single user/doc process
state = ProcessingState()
