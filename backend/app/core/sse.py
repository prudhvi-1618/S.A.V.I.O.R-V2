import json
from typing import Any, Dict

class SSEEventBuilder:
    @staticmethod
    def format_event(event: str, data: Dict[str, Any]) -> str:
        data_str = json.dumps(data)
        return f"event: {event}\ndata: {data_str}\n\n"
