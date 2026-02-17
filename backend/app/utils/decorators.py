"""
Utility decorators for safe task execution with error handling.
"""
import functools
import logging
from celery.exceptions import SoftTimeLimitExceeded

logger = logging.getLogger(__name__)


def safe_task(func):
    """
    Decorator to make Celery tasks crash-resistant.
    Catches all exceptions and returns error status instead of crashing.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SoftTimeLimitExceeded:
            logger.error(f"Task {func.__name__} exceeded time limit")
            return {
                "status": "timeout",
                "error": "Task execution exceeded time limit"
            }
        except Exception as e:
            logger.exception(f"Task {func.__name__} failed with error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_name": func.__name__
            }
    return wrapper


def safe_api_call(fallback_value=None):
    """
    Decorator for API calls that should not crash the application.
    Returns fallback_value if the call fails.
    
    Usage:
        @safe_api_call(fallback_value=[])
        def get_leads():
            return external_api.get_leads()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API call {func.__name__} failed: {str(e)}")
                return fallback_value
        return wrapper
    return decorator


def retry_on_failure(max_attempts=3, delay=1):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay in seconds between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}"
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            # All attempts failed
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator
