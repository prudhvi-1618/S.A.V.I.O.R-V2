from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
from typing import List
from dataclasses import dataclass
from app.state.processing_state import ChunkData

@dataclass
class SearchResult:
    chunk_id: str
    chunk_text: str
    score: float
    page_numbers: List[int]
    primary_page: int
    element_types: List[str]
    element_ids: List[str]
    chunk_type: str
    image_path: str | None
    image_description: str | None
    coordinates: List[dict] | None

class QdrantService:
    client = QdrantClient(url=settings.QDRANT_URL)

    @classmethod
    def ensure_collection(cls):
        collections = cls.client.get_collections().collections
        exists = any(c.name == settings.QDRANT_COLLECTION for c in collections)
        if not exists:
            cls.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )

    @classmethod
    def reset_collection(cls):
        collections = cls.client.get_collections().collections
        exists = any(c.name == settings.QDRANT_COLLECTION for c in collections)
        if exists:
            cls.client.delete_collection(collection_name=settings.QDRANT_COLLECTION)
        cls.ensure_collection()

    @classmethod
    def upsert_chunk(cls, chunk: ChunkData, vector: List[float]):
        payload = {
            "chunk_id": chunk.chunk_id,
            "chunk_text": chunk.chunk_text,
            "chunk_index": chunk.chunk_index,
            "element_ids": chunk.element_ids,
            "element_types": chunk.element_types,
            "page_numbers": chunk.page_numbers,
            "primary_page": chunk.primary_page,
            "chunk_type": chunk.chunk_type,
            "image_path": chunk.image_path,
            "image_description": chunk.image_description,
            "coordinates": chunk.coordinates
        }
        point = PointStruct(
            id=chunk.qdrant_id,
            vector=vector,
            payload=payload
        )
        cls.client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[point]
        )

    @classmethod
    def upsert_chunks(cls, chunks: List[ChunkData], vectors: List[List[float]]):
        points = []
        for chunk, vector in zip(chunks, vectors):
            payload = {
                "chunk_id": chunk.chunk_id,
                "chunk_text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index,
                "element_ids": chunk.element_ids,
                "element_types": chunk.element_types,
                "page_numbers": chunk.page_numbers,
                "primary_page": chunk.primary_page,
                "chunk_type": chunk.chunk_type,
                "image_path": chunk.image_path,
                "image_description": chunk.image_description,
                "coordinates": chunk.coordinates
            }
            points.append(
                PointStruct(
                    id=chunk.qdrant_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        if points:
            cls.client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=points
            )

    @classmethod
    def search(
        cls,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.3
    ) -> List[SearchResult]:
        if hasattr(cls.client, "search"):
            results = cls.client.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
        else:
            response = cls.client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            results = response.points

        search_results = []
        for r in results:
            search_results.append(SearchResult(
                chunk_id=r.payload.get("chunk_id", ""),
                chunk_text=r.payload.get("chunk_text", ""),
                score=r.score,
                page_numbers=r.payload.get("page_numbers", []),
                primary_page=r.payload.get("primary_page", 0),
                element_types=r.payload.get("element_types", []),
                element_ids=r.payload.get("element_ids", []),
                chunk_type=r.payload.get("chunk_type", "text"),
                image_path=r.payload.get("image_path"),
                image_description=r.payload.get("image_description"),
                coordinates=r.payload.get("coordinates")
            ))
        return search_results

    @classmethod
    def health_check(cls) -> bool:
        """Check if Qdrant is accessible and healthy."""
        try:
            # We just need to hit an endpoint to check connectivity
            cls.client.get_collections()
            return True
        except Exception:
            return False
