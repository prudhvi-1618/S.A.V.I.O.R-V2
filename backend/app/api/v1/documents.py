from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.repositories.element_repository import ElementRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import Document
from app.state.state_manager import StateManager
from collections import defaultdict
import os
import uuid
import shutil
from datetime import datetime
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    document_id = str(uuid.uuid4())
    
    # Ensure upload directory exists
    os.makedirs("data/uploads", exist_ok=True)
    
    file_path = f"data/uploads/{document_id}.pdf"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc = Document(
            id=document_id,
            filename=file.filename,
            status="uploaded",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        DocumentRepository.create(doc)
        StateManager.save_state(document_id)
        
        return {"document_id": document_id, "filename": file.filename}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/{document_id}/file")
async def get_document_file(document_id: str):
    file_path = f"data/uploads/{document_id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/pdf", headers={"Content-Disposition": "inline"})

@router.get("/{document_id}/elements")
async def get_document_elements(document_id: str):
    elements = ElementRepository.get_by_document(document_id)
    if not elements:
        return []
    
    grouped = defaultdict(list)
    for el in elements:
        grouped[el.page_number].append(el.model_dump())
    
    result = []
    for page, items in sorted(grouped.items()):
        result.append({
            "page_number": page,
            "elements": items
        })
        
    return result

@router.get("/images/{filename}")
async def get_image(filename: str):
    file_path = f"data/extracted_images/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

