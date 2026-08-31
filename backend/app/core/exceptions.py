from typing import Any

class SaviorException(Exception):
    """Base exception for all S.A.V.I.O.R application errors."""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

class DocumentNotFoundError(SaviorException):
    """Raised when a requested document cannot be found."""
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID {document_id} not found",
            status_code=404,
            details={"document_id": document_id}
        )

class ProcessingError(SaviorException):
    """Raised when document processing fails."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=500, details=details)

class ExtractionError(ProcessingError):
    """Raised when document extraction fails."""
    pass

class EmbeddingError(SaviorException):
    """Raised when generating embeddings fails."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=502, details=details)

class VectorDatabaseError(SaviorException):
    """Raised when operations on the vector database fail."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=503, details=details)

class LLMGenerationError(SaviorException):
    """Raised when generating responses from the LLM fails."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=502, details=details)

class ValidationError(SaviorException):
    """Raised for input validation failures not caught by FastAPI."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=422, details=details)
