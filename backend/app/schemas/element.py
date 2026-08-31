from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ElementCoordinates(BaseModel):
    points: List[List[float]]
    page_width: float
    page_height: float

class ExtractedElement(BaseModel):
    element_id: str
    document_id: str
    element_type: str
    text: Optional[str] = None
    page_number: int
    coordinates: Optional[ElementCoordinates] = None
    metadata: Dict[str, Any] = {}
