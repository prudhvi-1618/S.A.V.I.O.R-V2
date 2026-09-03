import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class Settings:
    PROJECT_NAME: str = "S.A.V.I.O.R"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "savior_documents")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gemini-1.5-flash")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gemini-1.5-flash")
    GEMINI_TIMEOUT_MS: int = int(os.getenv("GEMINI_TIMEOUT_MS", "30000"))
    EMBEDDING_DIMENSION: int = 768
    
    # Retrieval Configuration
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "15"))
    RETRIEVAL_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.3"))
    RETRIEVAL_WEAK_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_WEAK_SCORE_THRESHOLD", "0.5"))
    RETRIEVAL_MAX_CONTEXT_CHARS: int = int(os.getenv("RETRIEVAL_MAX_CONTEXT_CHARS", "16000"))
    RETRIEVAL_MAX_CHUNK_CHARS: int = int(os.getenv("RETRIEVAL_MAX_CHUNK_CHARS", "1500"))
    
    # Processing Configuration
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "20"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

settings = Settings()
