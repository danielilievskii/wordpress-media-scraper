import logging
import aiohttp

from .fetcher import Fetcher
from .parser import Parser
from .http_client import HttpClient
from store import StoreFactory

logger = logging.getLogger(__name__)


class Scraper:
    """Class for orchestrating the scraping workflow for a single website"""

    def __init__(self, site_url: str, site_name: str):
        self.site_url = site_url
        self.site_name = site_name

        self._parser = Parser(self.site_url, self.site_name)
        self._store = StoreFactory.create(self.site_name)

    async def run(self):
        """
        Execute the full scraping pipeline by loading previously seen IDs,
        fetching site metadata and raw post data, parsing them into structured
        Article objects, and saving any new records. The process ensures duplicates
        are skipped and all results are persisted to the data store.
        """

        logger.info("=" * 80)
        logger.info("Starting scraper for %s", self.site_url)
        logger.info("=" * 80)

        async with aiohttp.ClientSession() as session:
            http_client = HttpClient(session=session)
            fetcher = Fetcher(self.site_url, self.site_name, http_client)

            logger.info("Loading previously seen IDs...")
            seen_ids = self._store.load_seen_ids()
            logger.info("Loaded %d previously seen IDs", len(seen_ids))

            logger.info("Fetching metadata...")
            metadata = await fetcher.fetch_metadata()

            logger.info("Fetching raw data...")
            raw_data = await fetcher.fetch_data(
                seen_ids=seen_ids,
                total_pages=metadata["total_pages"],
            )

            logger.info("Parsing data...")
            parsed_records = self._parser.parse(raw_data, metadata=metadata)
            logger.info("Parsed %d records", len(parsed_records))

            if parsed_records:
                logger.info("Saving %d new records...", len(parsed_records))
                self._store.save_articles(parsed_records)
                logger.info("Successfully saved %d records", len(parsed_records))
            else:
                logger.info("No new records to save")

        logger.info("=" * 80)
        logger.info("Scraping completed for %s", self.site_url)
        logger.info("=" * 80)