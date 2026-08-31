from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import dataclasses

from app.repositories.document_repository import DocumentRepository
from app.services.chat.chat_service import ChatService
from app.state.chat_state import get_chat_state

router = APIRouter(prefix="/chat", tags=["chat"])
doc_repo = DocumentRepository()

class ChatRequest(BaseModel):
    question: str

@router.post("/{document_id}/stream")
async def stream_chat(document_id: str, request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty.")
        
    doc = doc_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    from app.state.processing_state import get_processing_state
    state = get_processing_state(document_id)
    if state.status != "completed":
        raise HTTPException(status_code=409, detail="Document processing is not complete yet.")

    return StreamingResponse(
        ChatService.stream_answer(document_id, request.question),
        media_type="text/event-stream"
    )

@router.get("/{document_id}/trace")
async def get_retrieval_trace(document_id: str):
    doc = doc_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    chat_state = get_chat_state(document_id)
    if not hasattr(chat_state, "latest_trace") or not chat_state.latest_trace:
        raise HTTPException(status_code=404, detail="No retrieval trace found.")
        
    return dataclasses.asdict(chat_state.latest_trace)

@router.delete("/{document_id}/history")
async def clear_chat_history(document_id: str):
    doc = doc_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    chat_state = get_chat_state(document_id)
    chat_state.clear()
    
    return {"message": "Chat history cleared successfully."}
