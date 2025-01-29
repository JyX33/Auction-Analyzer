import asyncio
import time
import httpx
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager

class RateLimiter:
    """Enforces rate limits and concurrency constraints for API requests"""
    def __init__(self, max_concurrent: int = 20, req_per_second: int = 100):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request: Optional[float] = None
        self.min_interval = 1.0 / req_per_second

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
        """Execute a request with exponential backoff retry logic"""
        retry_delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                async with self.throttle():
                    return await coro
            except Exception as e:
                if attempt == max_retries or not self.is_retryable(e):
                    raise
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

    def is_retryable(self, error: Exception) -> bool:
        """Determine if a request should be retried based on Blizzard API error codes"""
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code in {429, 500, 502, 503, 504}
        return False
