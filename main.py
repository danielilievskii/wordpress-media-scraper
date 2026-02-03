import asyncio
import logging

from config import setup_logging, settings
from scraper import Scraper

logger = logging.getLogger(__name__)


async def main():
    """Entry point for the scraper application."""
    setup_logging()

    scrapers = [Scraper(site_url=url, site_name=name) for name, url in settings.site_registry]

    logger.info("=" * 80)
    logger.info("SCRAPING STARTED")
    logger.info("=" * 80)

    logger.info("Total sites to scrape: %d", len(scrapers))

    successful = 0
    failed = []

    for idx, scraper in enumerate(scrapers, start=1):
        logger.info(" ")
        logger.info("Processing site %d/%d: %s", idx, len(scrapers), scraper.site_name)

        try:
            await scraper.run()
            successful += 1
        except KeyboardInterrupt:
            logger.warning("Scraping interrupted by user at site: %s", scraper.site_name)
            raise
        except Exception as e:
            logger.error("Failed to scrape %s: %s", scraper.site_name, e, exc_info=True)
            failed.append(scraper.site_name)

    logger.info("=" * 80)
    logger.info("SCRAPING COMPLETED")
    logger.info("=" * 80)

    logger.info("Successfully scraped: %d/%d sites", successful, len(scrapers))

    if failed:
        logger.warning("Failed sites (%d): %s", len(failed), ", ".join(failed))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Scraping interrupted by user")
