import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, Optional

import httpx

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
        url = f"{self.base_url}/item/{item_id}?namespace=static-eu&locale=en_US"
        try:
            response = await self._request("GET", url)
            return {"results": [{"data": response}]}  # Match expected format
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"results": []}  # Return empty results for non-existent items
            raise

    async def fetch_connected_realms_index(self) -> list[int]:
        """Fetch list of all connected realm IDs"""
        url = f"{self.base_url}/connected-realm/index?namespace=dynamic-eu&locale=en_US"
        try:
            response = await self._request("GET", url)
            realms = []
            for realm in response.get("connected_realms", []):
                # Extract ID from href which looks like "https://.../data/wow/connected-realm/1234"
                try:
                    # Handle both full URLs and relative paths
                    href = realm.get("href", "")
                    # Remove query parameters and trailing slashes
                    clean_href = href.split("?")[0].rstrip("/")
                    parts = clean_href.split("/")
                    realm_id = int(parts[-1])
                    realms.append(realm_id)
                except (ValueError, IndexError) as e:
                    logging.warning(f"Failed to parse realm ID from href {href}: {e}")
                    continue
            if not realms:
                logging.warning(f"No realm IDs found in response: {response}")
            return realms
        except httpx.HTTPStatusError as e:
            logging.error(f"Failed to fetch connected realms index: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in fetch_connected_realms_index: {e}")
            return []

    async def fetch_connected_realm_details(self, realm_id: int) -> Optional[dict]:
        """Fetch details for a specific connected realm"""
        url = f"{self.base_url}/connected-realm/{realm_id}?namespace=dynamic-eu&locale=en_US"
        try:
            response = await self._request("GET", url)
            # Extract realm data with safer access and handle both string and dict values
            realms = response.get("realms", [])
            if not realms:
                logging.warning(f"No realms found for connected realm {realm_id}")
                return None

            first_realm = realms[0]

            realm_data = {
                "connected_realm_id": realm_id,
                "name": first_realm.get("slug", "unknown"),
                "population_type": response["population"].get("name", "unknown"),
                "realm_category": first_realm.get("category", "unknown"),
                "status": response.get("status", {}).get("name", "unknown"),
            }
            return realm_data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logging.warning(f"Connected realm {realm_id} not found")
                return None
            logging.error(f"Failed to fetch details for realm {realm_id}: {e}")
            raise

    async def fetch_auctions(
        self, connected_realm_id: int, items_ids: set[int]
    ) -> list[dict]:
        """Fetch auction house data for a connected realm."""
        url = f"{self.base_url}/connected-realm/{connected_realm_id}/auctions?namespace=dynamic-eu&locale=en_US"
        try:
            response = await self._request("GET", url)
            auctions = response.get("auctions", [])

            # Transform auction data to match our schema
            transformed_auctions = []
            for auction in auctions:
                try:
                    # Log raw auction data for debugging
                    logging.debug(f"Raw auction data: {auction}")

                    # Check if required fields exist
                    if "id" not in auction or "item" not in auction:
                        logging.warning(f"Auction missing required fields: {auction}")
                        continue

                    # Get item ID safely
                    item_id = auction["item"]["id"]

                    if not item_id:
                        logging.warning(
                            f"Could not extract item ID from auction: {auction}"
                        )
                        continue

                    if item_id not in items_ids:
                        logging.debug(
                            f"Skipping item ID {item_id} not in requested list"
                        )
                        continue

                    transformed_auction = {
                        "auction_id": auction["id"],
                        "connected_realm_id": connected_realm_id,
                        "item_id": item_id,
                        "buyout_price": auction.get(
                            "buyout", 0
                        ),  # Use 0 if no buyout price
                        "quantity": auction.get(
                            "quantity", 1
                        ),  # Default to 1 if not specified
                        "time_left": auction.get("time_left", ""),
                        "last_modified": datetime.utcnow(),  # Use current time as fallback
                    }
                    transformed_auctions.append(transformed_auction)
                    logging.debug(f"Transformed auction data: {transformed_auction}")
                except (KeyError, ValueError) as e:
                    logging.warning(
                        f"Failed to transform auction data: {e}, auction: {auction}"
                    )
                    continue

            return transformed_auctions
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logging.warning(f"No auctions found for realm {connected_realm_id}")
                return []
            logging.error(
                f"Failed to fetch auctions for realm {connected_realm_id}: {e}"
            )
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching auctions: {e}")
            return []

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
            logging.error(
                f"API request failed: {e.response.status_code} {e.response.text}"
            )
            raise
