from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ChatMessage:
    role: str
    content: str
    
class ChatState:
    def __init__(self, max_history: int = 10):
        self.messages: List[ChatMessage] = []
        self.max_history = max_history

    def add_user_message(self, content: str):
        self.messages.append(ChatMessage(role="user", content=content))
        self._trim_history()

    def add_assistant_message(self, content: str):
        self.messages.append(ChatMessage(role="assistant", content=content))
        self._trim_history()

    def get_history(self) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self):
        self.messages.clear()
        
    def _trim_history(self):
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

# Global chat state dictionary mapping document_id to ChatState
_chat_states: Dict[str, ChatState] = {}

def get_chat_state(document_id: str) -> ChatState:
    if document_id not in _chat_states:
        _chat_states[document_id] = ChatState()
    return _chat_states[document_id]
