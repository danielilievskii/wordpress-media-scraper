from typing import Any, Optional, Dict
import aiohttp
import asyncio
import logging
from utils import RateLimiter, retry_on_exception
from config import settings

logger = logging.getLogger(__name__)


class HttpClient:
    """
    HTTP client responsible for making requests with retry,
    rate limiting, and timeout handling.
    """

    def __init__(
            self,
            session: aiohttp.ClientSession,
            headers: Optional[Dict] = None,
            timeout: Optional[int] = None
    ):
        self.session = session
        self.headers = headers or settings.headers
        self.timeout = timeout or settings.request_timeout
        self.rate_limiter = RateLimiter(settings.requests_per_second)

    @retry_on_exception(
        max_retries=settings.max_retries,
        delay=settings.retry_delay,
        backoff=settings.retry_backoff,
        exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
    )
    async def fetch_json(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Any]:
        """Perform an HTTP GET request and return the parsed JSON response."""

        await self.rate_limiter.wait()

        merged_headers = {**self.headers, **(headers or {})}

        async with self.session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
        ) as response:
            if response.status == 429:
                wait_time = int(response.headers.get("Retry-After", 60))
                logger.warning("Rate limited. Waiting %d seconds.", wait_time)

                await asyncio.sleep(wait_time)
                raise aiohttp.ClientError("Rate limited, retrying.")

            response.raise_for_status()
            return await response.json()

    @retry_on_exception(
        max_retries=settings.max_retries,
        delay=settings.retry_delay,
        backoff=settings.retry_backoff,
        exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
    )
    async def fetch_json_with_headers(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Perform an HTTP GET request and return both the response payload and headers."""

        await self.rate_limiter.wait()
        merged_headers = {**self.headers, **(headers or {})}

        async with self.session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
        ) as response:
            response.raise_for_status()
            data = await response.json()

            return {
                "data": data,
                "headers": dict(response.headers),
            }
