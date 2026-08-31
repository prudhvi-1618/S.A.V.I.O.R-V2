from app.state.chat_state import ChatState, get_chat_state

def test_chat_state_add_messages():
    state = ChatState(max_history=5)
    
    state.add_user_message("Hello")
    assert len(state.get_history()) == 1
    assert state.get_history()[0]["role"] == "user"
    assert state.get_history()[0]["content"] == "Hello"
    
    state.add_assistant_message("Hi there")
    assert len(state.get_history()) == 2
    assert state.get_history()[1]["role"] == "assistant"
    
def test_chat_state_history_limit():
    state = ChatState(max_history=3)
    
    state.add_user_message("1")
    state.add_assistant_message("2")
    state.add_user_message("3")
    state.add_assistant_message("4")
    
    history = state.get_history()
    assert len(history) == 3
    assert history[0]["content"] == "2"
    assert history[1]["content"] == "3"
    assert history[2]["content"] == "4"

def test_chat_state_clear():
    state = ChatState()
    state.add_user_message("Hello")
    state.clear()
    assert len(state.get_history()) == 0

def test_get_chat_state():
    state1 = get_chat_state("doc1")
    state2 = get_chat_state("doc2")
    state1_again = get_chat_state("doc1")
    
    assert state1 is not state2
    assert state1 is state1_again
