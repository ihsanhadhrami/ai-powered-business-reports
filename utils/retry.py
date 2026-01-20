"""
Retry Mechanism Utilities
Provides decorators and utilities for automatic retry with exponential backoff.
"""

import time
import functools
from typing import Callable, Tuple, Type, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    
    Usage:
        @retry_with_backoff(max_retries=3, exceptions=(ConnectionError,))
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class RetryContext:
    """
    Context manager for retry logic with manual control.
    
    Usage:
        with RetryContext(max_retries=3) as retry:
            while retry.should_continue():
                try:
                    # your code
                    break
                except Exception as e:
                    retry.handle_exception(e)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempt = 0
        self.last_exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def should_continue(self) -> bool:
        """Check if we should continue trying."""
        return self.attempt <= self.max_retries
    
    def handle_exception(self, exception: Exception):
        """Handle an exception and prepare for retry."""
        self.last_exception = exception
        self.attempt += 1
        
        if self.attempt > self.max_retries:
            logger.error(f"All {self.max_retries + 1} attempts failed: {exception}")
            raise exception
        
        delay = min(self.base_delay * (2 ** (self.attempt - 1)), self.max_delay)
        logger.warning(f"Attempt {self.attempt}/{self.max_retries + 1} failed: {exception}. Retrying in {delay:.1f}s...")
        time.sleep(delay)
