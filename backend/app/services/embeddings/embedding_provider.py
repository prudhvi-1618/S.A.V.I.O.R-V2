from typing import List

from app.core.config import settings
from app.core.logging import get_logger
from app.services.vision.gemini_service import GeminiService

logger = get_logger(__name__)


class EmbeddingProvider:
    _hf_model = None

    @classmethod
    def generate_document_embedding(cls, text: str) -> List[float]:
        if cls._uses_gemini():
            return GeminiService.generate_embedding(text)
        if cls._uses_huggingface_local():
            return cls._generate_huggingface_embedding(text, is_query=False)
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")

    @classmethod
    def generate_query_embedding(cls, text: str) -> List[float]:
        if cls._uses_gemini():
            return GeminiService.generate_query_embedding(text)
        if cls._uses_huggingface_local():
            return cls._generate_huggingface_embedding(text, is_query=True)
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")

    @staticmethod
    def _uses_gemini() -> bool:
        return settings.EMBEDDING_PROVIDER in {"gemini", "google", "google_gemini"}

    @staticmethod
    def _uses_huggingface_local() -> bool:
        return settings.EMBEDDING_PROVIDER in {"huggingface_local", "hf_local", "local"}

    @classmethod
    def _get_huggingface_model(cls):
        if cls._hf_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "Local Hugging Face embeddings require sentence-transformers. "
                    "Run `uv sync` in the backend folder, then restart the backend."
                ) from exc

            kwargs = {"device": "cpu"}
            if settings.HF_TOKEN:
                kwargs["token"] = settings.HF_TOKEN

            logger.info(
                "Loading local Hugging Face embedding model: %s",
                settings.EMBEDDING_MODEL,
            )
            cls._hf_model = SentenceTransformer(settings.EMBEDDING_MODEL, **kwargs)
        return cls._hf_model

    @classmethod
    def _generate_huggingface_embedding(cls, text: str, *, is_query: bool) -> List[float]:
        model = cls._get_huggingface_model()
        normalized_text = text.strip()
        if not normalized_text:
            return [0.0] * settings.EMBEDDING_DIMENSION

        input_text = normalized_text
        if is_query and settings.EMBEDDING_MODEL.startswith("BAAI/bge-"):
            input_text = (
                "Represent this sentence for searching relevant passages: "
                f"{normalized_text}"
            )

        embedding = model.encode(
            input_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        vector = embedding.tolist()
        if len(vector) != settings.EMBEDDING_DIMENSION:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"model returned {len(vector)}, settings expect "
                f"{settings.EMBEDDING_DIMENSION}. Update EMBEDDING_DIMENSION."
            )
        return vector
