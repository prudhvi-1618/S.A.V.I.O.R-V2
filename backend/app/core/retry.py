import asyncio
import functools
import logging
from typing import Callable, Any, TypeVar, cast
from app.core.config import settings

T = TypeVar("T")
logger = logging.getLogger(__name__)

def with_retry(
    max_retries: int = settings.MAX_RETRIES,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}. Error: {e}")
                        raise
                    
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} in {delay}s due to: {e}")
                    await asyncio.sleep(delay)
                    
        return wrapper
    return decorator
