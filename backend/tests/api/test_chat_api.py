import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.state.chat_state import get_chat_state
from app.services.retrieval.retrieval_service import RetrievalResult
from app.services.retrieval.retrieval_trace import RetrievalTrace

client = TestClient(app)

@patch("app.api.v1.chat.ChatService.stream_answer")
def test_stream_chat_endpoint(mock_stream):
    # Mock the generator
    async def mock_generator(*args, **kwargs):
        yield "data: {\"test\": \"data\"}\n\n"
        
    mock_stream.return_value = mock_generator()
    
    response = client.post(
        "/api/v1/chat/doc_test_123/stream",
        json={"question": "What is this?"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    assert "data: {\"test\": \"data\"}" in response.text
    
def test_get_chat_trace_endpoint():
    # Setup state
    state = get_chat_state("doc_trace_test")
    
    trace = RetrievalTrace(
        question="Test",
        total_results=1,
        retrieved_chunks=[
            RetrievalResult("chunk1", "text1", 0.9, ["el1"], ["Text"], [1], 1, "text", None, None, [])
        ],
        context_preview="Preview"
    )
    
    state.save_trace(trace)
    
    response = client.get("/api/v1/chat/doc_trace_test/trace")
    assert response.status_code == 200
    
    data = response.json()
    assert data["question"] == "Test"
    assert data["total_results"] == 1
    assert len(data["retrieved_chunks"]) == 1
    assert data["retrieved_chunks"][0]["chunk_id"] == "chunk1"

def test_get_chat_trace_not_found():
    state = get_chat_state("doc_empty")
    state.clear()
    
    response = client.get("/api/v1/chat/doc_empty/trace")
    assert response.status_code == 404
