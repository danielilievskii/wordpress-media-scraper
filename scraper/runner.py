import logging
from typing import List

from .scraper import Scraper

logger = logging.getLogger(__name__)


async def run_scrapers(scrapers: List[Scraper]) -> None:
    """Run multiple scrapers sequentially and report success/failure."""

    logger.info("=" * 80)
    logger.info("STARTING MULTI-SITE SCRAPER")
    logger.info("=" * 80)
    logger.info("Total sites to scrape: %d", len(scrapers))

    successful = 0
    failed = []

    for idx, scraper in enumerate(scrapers):
        logger.info("Processing site %d/%d: %s", idx, len(scrapers), scraper.site_name)

        try:
            await scraper.run()
            successful += 1
            logger.info("Successfully scraped: %s", scraper.site_name)
        except KeyboardInterrupt:
            logger.warning("Scraping interrupted at site: %s", scraper.site_name)
            return
        except Exception as e:
            logger.error("✗ Failed to scrape %s: %s", scraper.site_name, e, exc_info=True)
            failed.append(scraper.site_name)
            continue

    logger.info("=" * 80)
    logger.info("SCRAPING COMPLETED")
    logger.info("")
    logger.info("Successfully scraped: %d/%d sites", successful, len(scrapers))

    if failed:
        logger.warning("Failed sites (%d): %s", len(failed), ", ".join(failed))

    logger.info("=" * 80)



