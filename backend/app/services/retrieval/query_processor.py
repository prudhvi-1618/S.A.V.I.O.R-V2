import re

class QueryProcessor:
    @staticmethod
    def normalize(query: str) -> str:
        """
        Normalizes a user query by:
        - Removing leading/trailing whitespace
        - Collapsing multiple spaces into a single space
        - Keeping it lowercase for keyword matching later
        """
        if not query:
            return ""
        
        # Strip leading/trailing
        query = query.strip()
        
        # Collapse whitespace
        query = re.sub(r'\s+', ' ', query)
        
        return query
