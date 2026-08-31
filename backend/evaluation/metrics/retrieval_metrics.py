from typing import List
from app.services.retrieval.retrieval_service import RetrievalResult

class RetrievalMetrics:
    @staticmethod
    def calculate_hit_rate(results: List[RetrievalResult], expected_types: List[str]) -> float:
        """
        Calculate if at least one of the expected element types was retrieved.
        (A simplified heuristic for Hit@K without labeled element IDs)
        """
        if not expected_types or not results:
            return 0.0
            
        expected_set = set(t.lower() for t in expected_types)
        
        for r in results:
            for et in r.element_types:
                if et.lower() in expected_set:
                    return 1.0
                    
        return 0.0

    @staticmethod
    def calculate_mrr(results: List[RetrievalResult], expected_types: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR) based on expected element types.
        """
        if not expected_types or not results:
            return 0.0
            
        expected_set = set(t.lower() for t in expected_types)
        
        for rank, r in enumerate(results, 1):
            for et in r.element_types:
                if et.lower() in expected_set:
                    return 1.0 / rank
                    
        return 0.0
