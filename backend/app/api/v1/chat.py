from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import dataclasses
import os
from datetime import datetime

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import Document
from app.services.chat.chat_service import ChatService
from app.state.chat_state import get_chat_state
from app.state.state_manager import StateManager

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str


def get_or_recover_document(document_id: str):
    doc = DocumentRepository.get(document_id)
    if doc:
        return doc

    if StateManager.load_state(document_id):
        doc = DocumentRepository.get(document_id)
        if doc:
            return doc

    file_path = f"data/uploads/{document_id}.pdf"
    if os.path.exists(file_path):
        return DocumentRepository.create(Document(
            id=document_id,
            filename=f"{document_id}.pdf",
            status="uploaded",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ))

    return None

@router.post("/{document_id}/stream")
async def stream_chat(document_id: str, request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty.")
        
    doc = get_or_recover_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return StreamingResponse(
        ChatService.stream_answer(document_id, request.question),
        media_type="text/event-stream"
    )

@router.get("/{document_id}/trace")
async def get_retrieval_trace(document_id: str):
    doc = get_or_recover_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    chat_state = get_chat_state(document_id)
    if not hasattr(chat_state, "latest_trace") or not chat_state.latest_trace:
        raise HTTPException(status_code=404, detail="No retrieval trace found.")
        
    return dataclasses.asdict(chat_state.latest_trace)

@router.delete("/{document_id}/history")
async def clear_chat_history(document_id: str):
    doc = get_or_recover_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    chat_state = get_chat_state(document_id)
    chat_state.clear()
    
    return {"message": "Chat history cleared successfully."}
