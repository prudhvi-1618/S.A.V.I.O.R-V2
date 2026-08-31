import json
from dataclasses import dataclass, asdict
from typing import List, AsyncGenerator
from app.state.processing_state import state as processing_state
from app.state.chat_state import get_chat_state
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalResult
from app.services.retrieval.context_builder import build_context
from app.services.retrieval.retrieval_trace import RetrievalTrace, TraceChunk
from app.services.vision.gemini_service import GeminiService
from app.core.sse import SSEEventBuilder

@dataclass
class ChatSource:
    source_id: str
    chunk_id: str
    element_id: str
    element_type: str
    page_number: int
    coordinates: List[dict] | None
    similarity_score: float
    preview: str
    image_path: str | None

class ChatService:
    @staticmethod
    async def stream_answer(document_id: str, question: str) -> AsyncGenerator[str, None]:
        # Step 1: Validate processing state
        if processing_state.embedding_status != "completed":
            yield SSEEventBuilder.format_event(
                event="chat_error",
                data={"error": "Document processing is not complete yet."}
            )
            return

        chat_state = get_chat_state(document_id)
        chat_state.add_user_message(question)

        try:
            # Step 2: Retrieve chunks
            yield SSEEventBuilder.format_event(
                event="retrieval_started",
                data={"question": question}
            )
            
            results = await RetrievalService.retrieve(question=question)
            
            # Step 3: Handle no results
            if not results:
                yield SSEEventBuilder.format_event(
                    event="retrieval_complete",
                    data={"total_results": 0}
                )
                
                msg = "I could not find relevant information in the uploaded document."
                yield SSEEventBuilder.format_event(event="answer_started", data={})
                yield SSEEventBuilder.format_event(event="answer_delta", data={"text": msg})
                yield SSEEventBuilder.format_event(event="sources", data={"sources": []})
                yield SSEEventBuilder.format_event(event="answer_complete", data={})
                chat_state.add_assistant_message(msg)
                return

            yield SSEEventBuilder.format_event(
                event="retrieval_complete",
                data={"total_results": len(results)}
            )

            # Step 4: Build retrieval trace and emit result events
            trace_chunks = []
            for rank, r in enumerate(results, 1):
                preview = r.image_description[:200] if r.chunk_type == "image" and r.image_description else r.chunk_text[:200]
                tc = TraceChunk(
                    rank=rank,
                    chunk_id=r.chunk_id,
                    similarity_score=r.score,
                    page_number=r.primary_page,
                    chunk_type=r.chunk_type,
                    element_ids=r.element_ids,
                    element_types=r.element_types,
                    content_preview=preview
                )
                trace_chunks.append(tc)
                
                yield SSEEventBuilder.format_event(
                    event="retrieval_result",
                    data=asdict(tc)
                )

            # Note: Trace doesn't need to be yielded as an event, but stored in state if we want to serve GET /trace
            # Actually, the user asked for GET /trace so we'll store it in chat_state or a separate trace_state
            # We'll just attach it to the chat_state temporarily
            
            # Step 5: Build context
            context = build_context(results)
            
            trace = RetrievalTrace(
                question=question,
                retrieved_chunks=trace_chunks,
                total_results=len(results),
                context_preview=context[:500] + "..."
            )
            chat_state.latest_trace = trace
            
            yield SSEEventBuilder.format_event(
                event="context_ready",
                data={"total_sources": len(results)}
            )

            # Detect weak retrieval
            top_score = results[0].score if results else 0
            from app.core.config import settings
            is_weak = top_score < settings.RETRIEVAL_WEAK_SCORE_THRESHOLD
            
            # Step 6: Generate answer sources
            sources = ChatService._create_sources(results)

            # Step 7: Stream Gemini response
            yield SSEEventBuilder.format_event(event="answer_started", data={})
            
            if is_weak:
                warning_msg = "Note: The retrieved information might not directly answer your question.\n\n"
                yield SSEEventBuilder.format_event(event="answer_delta", data={"text": warning_msg})
                
            full_answer = ""
            
            # Use strict grounding prompt wrapper
            grounding_prefix = (
                "You are an assistant answering questions based strictly on the provided document context. "
                "If the context does not contain the answer, say 'I cannot find the answer in the provided document.' "
                "Do not use outside knowledge. Do not hallucinate.\n\n"
            )
            
            for chunk_text in GeminiService.stream_chat_response(
                question=grounding_prefix + question,
                context=context,
                conversation_history=chat_state.get_history()[:-1]  # Exclude current user message from history, as we prepend it
            ):
                full_answer += chunk_text
                yield SSEEventBuilder.format_event(
                    event="answer_delta",
                    data={"text": chunk_text}
                )

            if is_weak:
                full_answer = warning_msg + full_answer

            chat_state.add_assistant_message(full_answer)

            # Emit sources
            yield SSEEventBuilder.format_event(
                event="sources",
                data={"sources": [asdict(s) for s in sources]}
            )
            
            yield SSEEventBuilder.format_event(event="answer_complete", data={})
            
        except Exception as e:
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"Chat error: {e}", exc_info=True)
            yield SSEEventBuilder.format_event(
                event="chat_error",
                data={"error": "Unable to generate an answer"}
            )

    @staticmethod
    def _create_sources(results: List[RetrievalResult]) -> List[ChatSource]:
        sources = []
        seen_elements = set()
        
        for idx, r in enumerate(results):
            # We create a source for each element in the chunk, avoiding duplicates
            for element_id, element_type in zip(r.element_ids, r.element_types):
                if element_id not in seen_elements:
                    seen_elements.add(element_id)
                    preview = r.image_description[:200] if r.chunk_type == "image" and r.image_description else r.chunk_text[:200]
                    sources.append(ChatSource(
                        source_id=f"source_{idx}_{element_id}",
                        chunk_id=r.chunk_id,
                        element_id=element_id,
                        element_type=element_type,
                        page_number=r.primary_page,
                        coordinates=r.coordinates,
                        similarity_score=r.score,
                        preview=preview,
                        image_path=r.image_path
                    ))
        return sources
