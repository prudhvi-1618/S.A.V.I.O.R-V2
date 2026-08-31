import logging
import sys
from contextvars import ContextVar
from typing import Any
import json

request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)

class StructuredLogger(logging.Logger):
    def _log(self, level: int, msg: Any, args: Any, exc_info: Any = None, extra: dict | None = None, stack_info: bool = False, stacklevel: int = 1) -> None:
        request_id = request_id_ctx_var.get()
        if extra is None:
            extra = {}
        if request_id:
            extra["request_id"] = request_id
            
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging():
    logging.setLoggerClass(StructuredLogger)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # Set uvicorn loggers to use our formatter
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers = [console_handler]
        logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
