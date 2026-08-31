from typing import Dict, List
from app.schemas.element import ExtractedElement

class ElementRepository:
    _store: Dict[str, ExtractedElement] = {}

    @classmethod
    def save(cls, element: ExtractedElement) -> ExtractedElement:
        cls._store[element.element_id] = element
        return element

    @classmethod
    def get_by_document(cls, document_id: str) -> List[ExtractedElement]:
        return [elem for elem in cls._store.values() if elem.document_id == document_id]
