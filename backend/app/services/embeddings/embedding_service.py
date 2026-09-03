import asyncio
from typing import List, AsyncGenerator
from uuid import uuid4
from app.state.processing_state import ChunkData, ProcessingState
from app.core.sse import SSEEventBuilder
from app.services.vision.gemini_service import GeminiService
from app.services.embeddings.qdrant_service import QdrantService

import hashlib
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    @staticmethod
    async def embed_all_chunks(
        chunks: List[ChunkData],
        state: ProcessingState
    ) -> AsyncGenerator[str, None]:
        try:
            await asyncio.to_thread(QdrantService.reset_collection)
            
            state.embedding_status = "processing"
            
            yield SSEEventBuilder.format_event("embedding_started", {
                "total_chunks": len(chunks)
            })

            # Cache for deduplication
            seen_hashes = {}
            
            # Batch collections
            batch_chunks = []
            batch_vectors = []
            batch_size = settings.EMBEDDING_BATCH_SIZE
            print(f"-------- Starting embedding process for {len(chunks)} chunks with batch size {batch_size} ---------- ", flush=True)
            for i, chunk in enumerate(chunks):
                text_to_embed = ""
                if chunk.chunk_type == "image":
                    yield SSEEventBuilder.format_event("processing_image", {
                        "chunk_id": chunk.chunk_id,
                        "image_path": chunk.image_path,
                        "page_number": chunk.primary_page
                    })
                    
                    description = await asyncio.to_thread(
                        GeminiService.describe_image, chunk.image_path
                    )
                    chunk.image_description = description.to_retrieval_text()
                    text_to_embed = chunk.image_description
                else:
                    text_to_embed = chunk.chunk_text

                # clean text
                if text_to_embed:
                    text_to_embed = " ".join(text_to_embed.split())
                    if len(text_to_embed) > 5000:  # arbitrary truncation to fit token limit safely
                        text_to_embed = text_to_embed[:5000]
                        
                # Deduplication logic
                content_hash = hashlib.md5(text_to_embed.encode('utf-8')).hexdigest() if text_to_embed else ""
                
                if content_hash in seen_hashes:
                    logger.info(f"Skipping embedding for chunk {chunk.chunk_id} - duplicate content")
                    vector = seen_hashes[content_hash]
                else:
                    # Generate embedding
                    logger.info(
                        "Embedding chunk %d/%d (%s)",
                        i + 1,
                        len(chunks),
                        chunk.chunk_id,
                    )
                    vector = await asyncio.to_thread(
                        GeminiService.generate_embedding, text_to_embed
                    )
                    logger.info("Embedding completed for chunk %d/%d", i + 1, len(chunks))
                    if content_hash:
                        seen_hashes[content_hash] = vector

                chunk.qdrant_id = str(uuid4())
                
                # Add to batch
                batch_chunks.append(chunk)
                batch_vectors.append(vector)
                
                # Flush batch if full
                if len(batch_chunks) >= batch_size:
                    logger.info("Upserting %d embedded chunks to Qdrant", len(batch_chunks))
                    await asyncio.to_thread(QdrantService.upsert_chunks, batch_chunks, batch_vectors)
                    logger.info("Qdrant upsert completed for %d chunks", len(batch_chunks))
                    batch_chunks = []
                    batch_vectors = []
                
                chunk.embedded = True
                state.update_embedding_progress(i + 1, len(chunks))

                yield SSEEventBuilder.format_event("chunk_embedded", {
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "chunk_type": chunk.chunk_type,
                    "page_number": chunk.primary_page,
                    "embedded_count": i + 1,
                    "total_chunks": len(chunks),
                    "element_ids": chunk.element_ids
                })

                if (i + 1) % 3 == 0:
                    await asyncio.sleep(0.01)

            # Flush remaining batch
            if batch_chunks:
                logger.info("Upserting final %d embedded chunks to Qdrant", len(batch_chunks))
                await asyncio.to_thread(QdrantService.upsert_chunks, batch_chunks, batch_vectors)
                logger.info("Final Qdrant upsert completed")

            state.embedding_status = "completed"
            yield SSEEventBuilder.format_event("embedding_complete", {
                "total_chunks": len(chunks),
                "total_vectors": len(chunks),
                "collection": "savior_documents"
            })

            print(f"-------- Finished embedding process for {len(chunks)} chunks ---------- ", flush=True)
            
        except Exception as e:
            state.embedding_status = "failed"
            logger.error(f"Error in embedding pipeline: {e}", exc_info=True)
            yield SSEEventBuilder.format_event("embedding_error", {
                "error": str(e)
            })
            raise
