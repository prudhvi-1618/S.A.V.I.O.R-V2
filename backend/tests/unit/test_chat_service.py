import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.chat.chat_service import ChatService
from app.state.chat_state import get_chat_state
from app.services.retrieval.retrieval_service import RetrievalResult

@pytest.mark.asyncio
@patch("app.services.chat.chat_service.RetrievalService.retrieve")
@patch("app.services.chat.chat_service.GeminiService.stream_chat_response")
async def test_handle_chat_stream(mock_stream, mock_retrieve):
    # Setup mocks
    mock_retrieve.return_value = [
        RetrievalResult("chunk1", "text1", 0.9, ["el1"], ["Text"], [1], 1, "text", None, None, [])
    ]
    
    # Async generator for mock_stream
    async def mock_generator(*args, **kwargs):
        yield "Hello"
        yield " World"
        
    mock_stream.return_value = mock_generator()
    
    # Get the state and clear it
    state = get_chat_state("doc_test")
    state.clear()
    
    # Run the generator
    events = []
    async for event in ChatService.stream_answer("doc_test", "What is this?"):
        events.append(event)
        
    # Analyze the events
    # Should contain: retrieval_started, retrieval_complete, answer_delta x2, sources, answer_complete
    
    event_names = []
    for evt in events:
        lines = evt.strip().split('\n')
        for line in lines:
            if line.startswith("event: "):
                event_names.append(line.replace("event: ", ""))
                
    assert "retrieval_started" in event_names
    assert "retrieval_complete" in event_names
    assert event_names.count("answer_delta") == 2
    assert "sources" in event_names
    assert "answer_complete" in event_names
    
    # Verify state update
    history = state.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "What is this?"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hello World"
    
    # Verify trace saved
    trace = state.get_last_trace()
    assert trace is not None
    assert trace.question == "What is this?"
    assert len(trace.retrieved_chunks) == 1
    assert trace.retrieved_chunks[0].chunk_id == "chunk1"
