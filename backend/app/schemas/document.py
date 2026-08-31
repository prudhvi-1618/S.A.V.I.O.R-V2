from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Document(BaseModel):
    id: str
    filename: str
    status: str = "uploaded" # uploaded, processing, completed, failed
    created_at: datetime
    updated_at: datetime
    total_elements: int = 0
    pages_processed: int = 0
    error: Optional[str] = None
