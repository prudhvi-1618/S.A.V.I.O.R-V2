from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from app.services.extraction.element_processor import ElementProcessor
from app.repositories.document_repository import DocumentRepository
from app.state.processing_state import state
from datetime import datetime
from app.schemas.document import Document
import os

router = APIRouter(prefix="/processing", tags=["processing"])

def _load_document(document_id: str):
    doc = DocumentRepository.get(document_id)
    if not doc:
        from app.state.state_manager import StateManager
        if StateManager.load_state(document_id):
            doc = DocumentRepository.get(document_id)
    return doc

@router.post("/{document_id}/start")
async def start_processing(request: Request, document_id: str):
    doc = _load_document(document_id)

    file_path = f"data/uploads/{document_id}.pdf"

    # Recover uploads created before document metadata persistence was added.
    if not doc and os.path.exists(file_path):
        doc = DocumentRepository.create(Document(
            id=document_id,
            filename=f"{document_id}.pdf",
            status="uploaded",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ))

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # If the document is already processed, bypass the pipeline
    if doc.status == "completed":
        return StreamingResponse(
            ElementProcessor.replay_document_state(document_id),
            media_type="text/event-stream",
        )

    if doc.status in {"processing", "extracted"}:
        raise HTTPException(
            status_code=409,
            detail="Document processing is already in progress",
        )
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document file not found")

    DocumentRepository.update(document_id, {"status": "processing"})
    
    return StreamingResponse(
        ElementProcessor.process_document(document_id, file_path),
        media_type="text/event-stream",
    )

@router.get("/{document_id}/status")
async def get_processing_status(document_id: str):
    doc = _load_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "status": doc.status}

@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str):
    chunks = state.chunks
    formatted_chunks = []
    for c in chunks:
        formatted_chunks.append({
            "chunk_id": c.chunk_id,
            "chunk_text": c.chunk_text[:200] + "..." if len(c.chunk_text) > 200 else c.chunk_text,
            "chunk_type": c.chunk_type,
            "page_numbers": c.page_numbers,
            "element_types": c.element_types,
            "embedded": c.embedded,
            "image_description": (c.image_description[:200] + "...") if c.image_description and len(c.image_description) > 200 else c.image_description
        })
    return {
        "total_chunks": state.total_chunks,
        "chunks": formatted_chunks
    }

@router.get("/{document_id}/elements/{element_id}/chunk")
async def get_element_chunk(document_id: str, element_id: str):
    chunk = state.get_chunk_by_element_id(element_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found for element")
    return {
        "chunk_id": chunk.chunk_id,
        "chunk_text": chunk.chunk_text,
        "chunk_type": chunk.chunk_type,
        "embedded": chunk.embedded,
        "image_description": chunk.image_description
    }
