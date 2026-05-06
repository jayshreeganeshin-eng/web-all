"""
Retry utilities for web-all.
Implements exponential backoff with jitter for resilient operations.
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging
from typing import Type, Tuple

logger = logging.getLogger(__name__)


# Common exceptions that should trigger retries
RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def get_retry_decorator(
    max_attempts: int = 5,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    jitter: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS
):
    """
    Create a retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries in seconds
        max_wait: Maximum wait time between retries in seconds
        jitter: Random jitter factor (0.0 to 1.0)
        exceptions: Tuple of exception types that should trigger retries
    
    Returns:
        A retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(initial=min_wait, max=max_wait, jitter=jitter),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


# Pre-configured retry decorators for common use cases

# Standard retry for HTTP requests
retry_http = get_retry_decorator(
    max_attempts=5,
    min_wait=1.0,
    max_wait=30.0
)

# Aggressive retry for critical operations
retry_critical = get_retry_decorator(
    max_attempts=10,
    min_wait=2.0,
    max_wait=120.0
)

# Light retry for non-critical operations
retry_light = get_retry_decorator(
    max_attempts=3,
    min_wait=0.5,
    max_wait=10.0
)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 5,
        min_wait: float = 1.0,
        max_wait: float = 60.0,
        jitter: float = 0.1,
        retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
    
    def get_decorator(self):
        """Get a retry decorator with this configuration."""
        return get_retry_decorator(
            max_attempts=self.max_attempts,
            min_wait=self.min_wait,
            max_wait=self.max_wait,
            jitter=self.jitter,
            exceptions=self.retryable_exceptions
        )
