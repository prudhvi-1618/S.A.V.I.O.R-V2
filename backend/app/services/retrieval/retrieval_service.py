from dataclasses import dataclass
from typing import List, Set
import asyncio

from app.services.embeddings.embedding_provider import EmbeddingProvider
from app.services.embeddings.qdrant_service import QdrantService
from app.services.retrieval.query_processor import QueryProcessor
from app.services.retrieval.reranker import HeuristicReranker
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class RetrievalResult:
    chunk_id: str
    chunk_text: str
    score: float
    element_ids: List[str]
    element_types: List[str]
    page_numbers: List[int]
    primary_page: int
    chunk_type: str
    image_path: str | None
    image_description: str | None
    coordinates: List[dict] | None

class RetrievalService:
    @staticmethod
    async def retrieve(
        question: str,
        limit: int = settings.RETRIEVAL_TOP_K,
        score_threshold: float = settings.RETRIEVAL_SCORE_THRESHOLD
    ) -> List[RetrievalResult]:
        
        # 1. Query Normalization
        normalized_query = QueryProcessor.normalize(question)
        logger.info(f"Retrieving chunks for query: '{normalized_query}'")

        loop = asyncio.get_event_loop()
        query_vector = await loop.run_in_executor(
            None,
            EmbeddingProvider.generate_query_embedding,
            normalized_query
        )

        # 2. Vector Search (ask for double the limit to allow for deduplication/filtering drops)
        search_results = await loop.run_in_executor(
            None,
            lambda: QdrantService.search(
                query_vector=query_vector,
                limit=limit * 2, 
                score_threshold=score_threshold
            )
        )

        # 3. Deduplication (by element_id to avoid redundant information)
        seen_element_ids: Set[str] = set()
        deduplicated_results = []
        
        for r in search_results:
            # Check if we already have the primary element
            has_new_content = False
            for e_id in r.element_ids:
                if e_id not in seen_element_ids:
                    has_new_content = True
                    seen_element_ids.add(e_id)
            
            if has_new_content:
                deduplicated_results.append(r)
                if len(deduplicated_results) >= limit:
                    break
                    
        logger.info(f"Retrieved {len(search_results)} chunks, deduplicated to {len(deduplicated_results)}")

        # 4. Heuristic Reranking
        reranked_results = HeuristicReranker.rerank(normalized_query, deduplicated_results)

        # Map to RetrievalResult
        results = []
        for r in reranked_results:
            results.append(RetrievalResult(
                chunk_id=r.chunk_id,
                chunk_text=r.chunk_text,
                score=r.score,
                element_ids=r.element_ids,
                element_types=r.element_types,
                page_numbers=r.page_numbers,
                primary_page=r.primary_page,
                chunk_type=r.chunk_type,
                image_path=r.image_path,
                image_description=r.image_description,
                coordinates=r.coordinates
            ))

        return results
