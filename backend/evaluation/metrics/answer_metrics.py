from typing import List

class AnswerMetrics:
    @staticmethod
    def calculate_keyword_coverage(answer: str, expected_keywords: List[str]) -> float:
        """
        Calculate the percentage of expected keywords present in the answer.
        Note: Keyword matching is a simple development metric and is not a complete 
        measure of answer correctness. True correctness requires LLM-as-a-judge 
        or human evaluation.
        """
        if not expected_keywords:
            return 1.0
            
        if not answer:
            return 0.0
            
        answer_lower = answer.lower()
        
        matches = 0
        for kw in expected_keywords:
            if kw.lower() in answer_lower:
                matches += 1
                
        return matches / len(expected_keywords)
