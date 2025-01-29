import httpx
import logging
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager
from .rate_limiter import RateLimiter

class BlizzardAPIClient:
    """Dedicated client for Blizzard API interactions"""
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://eu.api.blizzard.com/data/wow"
        self.rate_limiter = RateLimiter()
        self.access_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[httpx.AsyncClient]:
        """Context manager for API sessions with auth and rate limiting"""
        async with httpx.AsyncClient() as client:
            try:
                if not self.access_token:
                    await self.authenticate(client)
                self._client = client
                yield client
            finally:
                self._client = None

    async def authenticate(self, client: httpx.AsyncClient):
        """Obtain and refresh OAuth token"""
        auth_url = "https://oauth.battle.net/token"
        response = await client.post(
            auth_url,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
        )
        response.raise_for_status()
        self.access_token = response.json()["access_token"]

    async def fetch_item(self, item_id: int) -> dict:
        """Fetch item data with retry logic"""
        url = f"{self.base_url}/search/item?id={item_id}"
        return await self._request("GET", url)

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        """Execute API request with rate limiting and error handling"""
        if not self._client:
            raise RuntimeError("Client not initialized - use session context manager")

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            response = await self.rate_limiter.execute_with_retry(
                self._client.request(method, url, headers=headers, **kwargs)
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"API request failed: {e.response.status_code} {e.response.text}")
            raise
