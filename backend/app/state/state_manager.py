import json
import os
from dataclasses import asdict
from typing import List, Optional
from datetime import datetime
from app.repositories.element_repository import ElementRepository
from app.repositories.document_repository import DocumentRepository
from app.state.processing_state import state, ChunkData
from app.schemas.element import ExtractedElement
from app.schemas.document import Document

class StateManager:
    BASE_DIR = "data/state"

    @classmethod
    def _get_file_path(cls, document_id: str) -> str:
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        return os.path.join(cls.BASE_DIR, f"{document_id}.json")

    @classmethod
    def save_state(cls, document_id: str):
        doc = DocumentRepository.get(document_id)
        if not doc:
            return

        elements = ElementRepository.get_by_document(document_id)
        chunks = state.chunks

        data = {
            "document": doc.model_dump(mode='json'),
            "elements": [el.model_dump(mode='json') for el in elements],
            "chunks": [asdict(c) for c in chunks],
            "total_chunks": state.total_chunks,
            "embedded_chunks": state.embedded_chunks
        }

        file_path = cls._get_file_path(document_id)
        temp_file_path = f"{file_path}.tmp"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file_path, file_path)

    @classmethod
    def load_state(cls, document_id: str) -> bool:
        """Loads state from file into memory. Returns True if successful."""
        file_path = cls._get_file_path(document_id)
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. Restore Document
            doc_data = data["document"]
            # datetime strings from json need to be parsed by Pydantic
            doc = Document(**doc_data)
            DocumentRepository.create(doc)

            # 2. Restore Elements
            for el_data in data.get("elements", []):
                el = ExtractedElement(**el_data)
                ElementRepository.save(el)

            # 3. Restore Chunks
            state.chunks = []
            for c_data in data.get("chunks", []):
                chunk = ChunkData(**c_data)
                state.chunks.append(chunk)
            
            state.total_chunks = data.get("total_chunks", 0)
            state.embedded_chunks = data.get("embedded_chunks", 0)
            
            return True
        except Exception as e:
            print(f"Error loading state for {document_id}: {e}")
            return False
