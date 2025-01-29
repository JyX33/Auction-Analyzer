import asyncio
import time
import random
import logging
import httpx
from typing import Optional
from contextlib import asynccontextmanager

class RateLimiter:
    """Enforces rate limits and concurrency constraints for API requests"""
    def __init__(self, max_concurrent: int = 20, req_per_second: int = 100):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request: Optional[float] = None
        self.min_interval = 1.0 / req_per_second
        self.remaining_requests = req_per_second
        self.reset_time: Optional[float] = None

    @asynccontextmanager
    async def throttle(self):
        """Context manager for rate-limited API calls"""
        async with self.semaphore:
            now = time.monotonic()
            if self.last_request is not None:
                elapsed = now - self.last_request
                if elapsed < self.min_interval:
                    await asyncio.sleep(self.min_interval - elapsed)
            
            self.last_request = now
            try:
                yield
            finally:
                self.last_request = time.monotonic()

    async def execute_with_retry(self, coro, max_retries: int = 3):
        """Execute request with Blizzard-specific rate limit handling"""
        retry_delay = 1.0
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                async with self.throttle():
                    # Execute the coroutine as is
                    response = await coro
                    if hasattr(response, 'headers'):
                        self._update_limits_from_headers(response.headers)
                    return response
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    retry_after = e.response.headers.get("Retry-After", "1")
                    retry_delay = float(retry_after) + 0.5  # Add buffer
                    logging.warning(f"Rate limited. Retrying in {retry_delay}s")
                elif not self.is_retryable(e):
                    raise
                
                if attempt == max_retries:
                    logging.error(f"Max retries ({max_retries}) reached. Last error: {e}")
                    raise
                    
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5 + random.uniform(0, 0.1), 30.0)  # Exponential backoff with jitter and max delay
            except Exception as e:
                logging.error(f"Unexpected error during request: {e}")
                raise
        
        if last_error:
            raise last_error
        raise RuntimeError("Request failed after all retries")

    def is_retryable(self, error: Exception) -> bool:
        """Determine if a request should be retried based on Blizzard API error codes"""
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code in {429, 500, 502, 503, 504}
        return False

    def _update_limits_from_headers(self, headers: dict):
        """Parse Blizzard rate limit headers and adjust limits"""
        limit = int(headers.get("x-account-ratelimit-limit", 100))
        remaining = int(headers.get("x-account-ratelimit-remaining", limit))
        reset_seconds = int(headers.get("x-account-ratelimit-reset", 1))
        
        self.remaining_requests = remaining
        self.reset_time = time.monotonic() + reset_seconds
        
        # Dynamically adjust rate limiting parameters
        self.min_interval = max(1.0 / limit, 0.01)  # At least 10ms between requests
        
        if remaining < 5:  # Add buffer when approaching limit
            self.min_interval *= 1.2
            logging.warning(f"Rate limit buffer activated. {remaining} requests remaining")
