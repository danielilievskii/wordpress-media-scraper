from typing import Any, Optional, Dict, List, Set
import logging
import asyncio

from config import settings
from .http_client import HttpClient

logger = logging.getLogger(__name__)


class Fetcher:
    """
    Scraper logic layer responsible for pagination, concurrency strategy,
    incremental scraping, and site-specific endpoints.

    This class delegates all HTTP/networking concerns to HttpClient.
    """

    def __init__(self, site_url: str, site_name: str, http_client: HttpClient):
        self.site_url = site_url
        self.site_name = site_name
        self.http = http_client

        # WordPress REST API endpoints
        self.posts_url = settings.posts_url.format(site_url=site_url)
        self.categories_url = settings.categories_url.format(site_url=site_url)

    async def fetch_metadata(self) -> Optional[Dict[str, Any]]:
        """Fetch metadata required for scraping, such as total page count and categories."""

        total_pages = await self.fetch_total_pages()
        categories = await self.fetch_categories()

        return {
            "total_pages": total_pages,
            "category_map": categories,
        }

    async def fetch_data(self, total_pages: int, seen_ids: Optional[Set[str]] = None, start_page: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch content using either concurrent or sequential strategy.

        Uses concurrent fetching when no existing IDs are provided (first run),
        otherwise uses sequential fetching with early stopping.
        """
        is_first_run = not seen_ids

        if is_first_run:
            logger.info("First run detected - using concurrent fetching.")
            return await self.fetch_all_concurrent(total_pages, start_page)
        else:
            logger.info("Incremental run detected - using sequential fetching.")
            return await self.fetch_all_sequential(
                total_pages=total_pages,
                existing_ids=seen_ids,
                start_page=start_page
            )

    async def fetch_all_concurrent(self, total_pages: int, start_page: int = 1) -> List[Dict]:
        """Fetch all pages concurrently with controlled concurrency."""

        logger.info("Fetching %d pages concurrently (max %d at a time).",total_pages, settings.max_concurrent_requests)

        all_articles: List[Dict] = []
        semaphore = asyncio.Semaphore(settings.max_concurrent_requests)

        async def fetch_with_semaphore(page: int) -> Optional[List[Dict]]:
            async with semaphore:
                return await self.fetch_page(page)

        tasks = [
            fetch_with_semaphore(page)
            for page in range(start_page, start_page + total_pages)
        ]

        completed = 0
        for coro in asyncio.as_completed(tasks):
            articles = await coro
            completed += 1

            if articles:
                all_articles.extend(articles)

            logger.info("Progress: %d/%d pages completed, %d total articles.",completed, total_pages, len(all_articles))

        return all_articles

    async def fetch_all_sequential(self, total_pages: int, existing_ids: Set[str], start_page: int = 1) -> List[Dict]:
        """Fetch pages sequentially with early stopping for incremental scraping."""

        logger.info("Fetching sequentially from page %d, stopping on duplicates.",start_page)

        all_new_articles: List[Dict] = []

        for page in range(start_page, start_page + total_pages):
            items = await self.fetch_page(page)

            if not items:
                logger.warning("No items returned for page %d - stopping.", page)
                break

            new_items = [
                item for item in items
                if f"{self.site_name}_{item.get('id')}" not in existing_ids
            ]

            duplicate_items = [
                item for item in items
                if f"{self.site_name}_{item.get('id')}" in existing_ids
            ]

            logger.info("Page %d: %d new items, %d already scraped.", page, len(new_items), len(duplicate_items))

            all_new_articles.extend(new_items)

            if not new_items and duplicate_items:
                logger.info("All items on page %d already exist - stopping scraping.", page)
                logger.info("Total pages fetched: %d/%d, total new items: %d.",page - start_page + 1, total_pages, len(all_new_articles))
                break

        return all_new_articles

    async def fetch_page(self, page: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch posts from a specific page of the WordPress REST API."""

        params = {
            "per_page": settings.posts_per_page,
            "page": page,
        }

        data = await self.http.fetch_json(self.posts_url, params)

        if data:
            logger.info("Fetched page %d with %d posts.", page, len(data))
            return data

        logger.warning("Failed to fetch page %d.", page)
        return None

    async def fetch_total_pages(self) -> int:
        """
        Fetch the total number of pages available from the WordPress REST API,
        using the ``X-WP-TotalPages`` response header.
        """

        try:
            params = {"per_page": settings.posts_per_page}
            result = await self.http.fetch_json_with_headers(self.posts_url, params)

            if result and "headers" in result:
                total_pages = int(result["headers"].get("X-WP-TotalPages", 1))
                logger.info("Total pages available: %d.", total_pages)
                return total_pages

        except Exception as e:
            logger.error("Error fetching total pages: %s", e)

        return 1

    async def fetch_categories(self) -> Dict[int, str]:
        """Fetch categories and build a mapping of category IDs to names."""

        category_map: Dict[int, str] = {}

        try:
            params = {"per_page": 100}
            data = await self.http.fetch_json(self.categories_url, params)

            if data:
                for cat in data:
                    category_map[cat["id"]] = cat["name"]
                logger.info("Fetched %d categories.", len(category_map))
            else:
                logger.warning("Failed to fetch categories.")

        except Exception as e:
            logger.error("Error building category map: %s", e)

        return category_map
