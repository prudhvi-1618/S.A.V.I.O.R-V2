from typing import Dict, Optional
from app.schemas.document import Document
from datetime import datetime

class DocumentRepository:
    _store: Dict[str, Document] = {}

    @classmethod
    def get(cls, document_id: str) -> Optional[Document]:
        return cls._store.get(document_id)

    @classmethod
    def create(cls, document: Document) -> Document:
        cls._store[document.id] = document
        return document

    @classmethod
    def update(cls, document_id: str, updates: dict) -> Optional[Document]:
        doc = cls.get(document_id)
        if doc:
            doc_data = doc.model_dump()
            doc_data.update(updates)
            doc_data["updated_at"] = datetime.now()
            updated_doc = Document(**doc_data)
            cls._store[document_id] = updated_doc
            return updated_doc
        return None
