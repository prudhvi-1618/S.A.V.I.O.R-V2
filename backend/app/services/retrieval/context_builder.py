from typing import List
from app.services.retrieval.retrieval_service import RetrievalResult
from app.core.config import settings

def build_context(results: List[RetrievalResult]) -> str:
    # Deduplicate chunk_ids to prevent sending the same chunk twice
    seen_chunks = set()
    unique_results = []
    
    for r in results:
        if r.chunk_id not in seen_chunks:
            seen_chunks.add(r.chunk_id)
            unique_results.append(r)
            
    # Sort by primary page number for coherent reading
    unique_results.sort(key=lambda x: x.primary_page)

    context_parts = []
    total_chars = 0
    
    for i, res in enumerate(unique_results):
        element_type = res.element_types[0] if res.element_types else "Unknown"
        
        source_header = (
            f"SOURCE {i + 1}\n"
            f"Chunk ID: {res.chunk_id}\n"
            f"Page: {res.primary_page}\n"
            f"Type: {element_type}\n"
        )
        
        if res.chunk_type == "image":
            content_section = f"Image Analysis:\n{res.image_description}"
        elif element_type == "Table":
            # Preserve some formatting for tables
            content_section = f"Table Data:\n{res.chunk_text}"
        elif element_type == "Title":
            content_section = f"Section Title:\n{res.chunk_text}"
        else:
            # Clean up excessive whitespace for text
            clean_text = " ".join(res.chunk_text.split())
            content_section = f"Content:\n{clean_text}"
            
        # Truncate individual chunk if it exceeds chunk limit
        max_chunk = settings.RETRIEVAL_MAX_CHUNK_CHARS
        if len(content_section) > max_chunk:
            content_section = content_section[:max_chunk] + "... [TRUNCATED]"
            
        chunk_str = f"{source_header}\n{content_section}"
        
        # Stop adding chunks if we hit the global context size limit
        if total_chars + len(chunk_str) > settings.RETRIEVAL_MAX_CONTEXT_CHARS:
            break
            
        context_parts.append(chunk_str)
        total_chars += len(chunk_str)

    # Join with separator
    return "\n\n" + "─" * 28 + "\n\n".join(context_parts)
