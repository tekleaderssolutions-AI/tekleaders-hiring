import asyncio
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)

def ai_retry(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Exponential backoff decorator for AI service calls.
    Ensures transient API failures don't break the 17-stage pipeline.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"AI Service failed after {max_retries} attempts: {str(e)}")
                        raise e
                    
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(f"AI Service attempt {retries} failed. Retrying in {delay}s... Error: {str(e)}")
                    await asyncio.sleep(delay)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
