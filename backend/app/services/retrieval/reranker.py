from typing import List
from app.services.embeddings.qdrant_service import SearchResult
import re

class HeuristicReranker:
    @staticmethod
    def rerank(query: str, results: List[SearchResult]) -> List[SearchResult]:
        """
        Reranks search results by giving a small boost to chunks 
        that contain exact keyword matches from the query.
        """
        if not results or not query:
            return results

        # Simple tokenizer (just alphanumeric)
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        # Remove common stop words for this naive approach
        stop_words = {"what", "is", "the", "a", "an", "of", "in", "and", "to", "for", "how", "why"}
        keywords = query_words - stop_words

        if not keywords:
            return results

        reranked = []
        for result in results:
            boost = 0.0
            chunk_text_lower = result.chunk_text.lower()
            
            # Very naive heuristic: count how many keywords are present
            matches = sum(1 for kw in keywords if kw in chunk_text_lower)
            
            # Boost score by up to 0.1 depending on keyword coverage
            if matches > 0:
                boost = (matches / len(keywords)) * 0.1
                
            # Create a new SearchResult with the boosted score
            # (Note: we just modify the score in place for simplicity here since it's a dataclass, 
            # but ideally we might want to preserve the original score for debugging)
            result.score = min(1.0, result.score + boost)
            reranked.append(result)
            
        # Re-sort by the new boosted score
        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked
