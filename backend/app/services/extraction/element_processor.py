import asyncio
from app.services.extraction.unstructured_service import UnstructuredService
from app.repositories.element_repository import ElementRepository
from app.repositories.document_repository import DocumentRepository
from app.core.sse import SSEEventBuilder
from app.state.processing_state import state
from app.services.chunking.chunking_service import ChunkingService
from app.services.embeddings.embedding_service import EmbeddingService

class ElementProcessor:
    @staticmethod
    async def process_document(document_id: str, file_path: str):
        try:
            # Yield initial status if needed, but the endpoint handles that.
            # Since unstructured can be blocking, we run it in a thread
            elements = await asyncio.to_thread(UnstructuredService.extract_elements, file_path, document_id)
            
            pages_processed = set()
            for el in elements:
                ElementRepository.save(el)
                pages_processed.add(el.page_number)
                
                yield SSEEventBuilder.format_event(
                    "element_extracted",
                    {
                        "element_id": el.element_id,
                        "element_type": el.element_type,
                        "text": el.text,
                        "page_number": el.page_number
                    }
                )
                await asyncio.sleep(0.01) # Small delay to simulate streaming if it's too fast

            DocumentRepository.update(document_id, {
                "status": "extracted",
                "total_elements": len(elements),
                "pages_processed": len(pages_processed)
            })

            yield SSEEventBuilder.format_event(
                "processing_complete",
                {
                    "document_id": document_id,
                    "total_elements": len(elements),
                    "pages_processed": len(pages_processed)
                }
            )

            # Step: Chunking
            yield SSEEventBuilder.format_event("chunking_started", {"document_id": document_id})
            chunks = ChunkingService.chunk_elements(state.get_all_elements())
            for chunk in chunks:
                state.add_chunk(chunk)
            yield SSEEventBuilder.format_event("chunking_complete", {
                "total_chunks": len(chunks)
            })

            # Step: Embedding
            async for event in EmbeddingService.embed_all_chunks(chunks, state):
                yield event

            DocumentRepository.update(document_id, {
                "status": "completed",
            })

            from app.state.state_manager import StateManager
            StateManager.save_state(document_id)

        except Exception as e:
            DocumentRepository.update(document_id, {
                "status": "failed",
                "error": str(e)
            })
            yield SSEEventBuilder.format_event(
                "processing_error",
                {
                    "error": str(e)
                }
            )

    @staticmethod
    async def replay_document_state(document_id: str):
        """Yields events from memory/cache for already processed documents."""
        # 1. Elements
        elements = ElementRepository.get_by_document(document_id)
        for el in elements:
            yield SSEEventBuilder.format_event(
                "element_extracted",
                {
                    "element_id": el.element_id,
                    "element_type": el.element_type,
                    "text": el.text,
                    "page_number": el.page_number
                }
            )
            await asyncio.sleep(0.005) # Prevent overloading client
        
        yield SSEEventBuilder.format_event(
            "processing_complete",
            {
                "document_id": document_id,
                "total_elements": len(elements),
                "pages_processed": len(set(el.page_number for el in elements))
            }
        )

        # 2. Chunks & Embeddings
        yield SSEEventBuilder.format_event("chunking_started", {"document_id": document_id})
        yield SSEEventBuilder.format_event("chunking_complete", {"total_chunks": state.total_chunks})
        
        yield SSEEventBuilder.format_event("embedding_started", {"total_chunks": state.total_chunks})
        
        for chunk in state.chunks:
            if chunk.embedded:
                yield SSEEventBuilder.format_event("chunk_embedded", {
                    "chunk_id": chunk.chunk_id,
                    "embedded_count": state.embedded_chunks,
                    "total_chunks": state.total_chunks
                })
        
        yield SSEEventBuilder.format_event("embedding_complete", {"document_id": document_id})
