import pytest
from unittest.mock import patch, MagicMock
from app.services.retrieval.retrieval_service import RetrievalService, RetrievalResult
from app.services.embeddings.qdrant_service import SearchResult

@pytest.mark.asyncio
@patch("app.services.vision.gemini_service.GeminiService.generate_query_embedding")
@patch("app.services.embeddings.qdrant_service.QdrantService.search")
async def test_retrieve(mock_search, mock_embed):
    # Mock embedding
    mock_embed.return_value = [0.1, 0.2, 0.3]
    
    # Mock Qdrant results
    mock_search.return_value = [
        SearchResult("chunk1", "text1", 0.8, [1], 1, ["Text"], ["el1"], "text", None, None, []),
        SearchResult("chunk2", "text2", 0.9, [2], 2, ["Table"], ["el2"], "text", None, None, []),
    ]
    
    results = await RetrievalService.retrieve("What is this?", limit=5)
    
    assert len(results) == 2
    assert isinstance(results[0], RetrievalResult)
    
    # Check ordering by score (descending)
    assert results[0].chunk_id == "chunk2"
    assert results[1].chunk_id == "chunk1"
    
    # Verify mock calls
    mock_embed.assert_called_once_with("What is this?")
    mock_search.assert_called_once_with(query_vector=[0.1, 0.2, 0.3], limit=5, score_threshold=0.3)

@pytest.mark.asyncio
@patch("app.services.vision.gemini_service.GeminiService.generate_query_embedding")
@patch("app.services.embeddings.qdrant_service.QdrantService.search")
async def test_retrieve_empty(mock_search, mock_embed):
    mock_embed.return_value = [0.1]
    mock_search.return_value = []
    
    results = await RetrievalService.retrieve("Empty test")
    
    assert len(results) == 0
