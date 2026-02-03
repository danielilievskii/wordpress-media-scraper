from typing import List
from pydantic_settings import BaseSettings


class ScraperSettings(BaseSettings):

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s %(levelname)s %(name)s | %(message)s"
    log_to_file: bool = False
    log_file_path: str = "scraper.log"

    # Registry of sites (name, url)
    site_registry: List[tuple[str, str]] = [
        ("irl", "https://irl.mk"),
        ("infomax", "https://infomax.mk"),
        ("kurir", "https://kurir.mk"),
        ("republika", "https://republika.mk"),
        ("centar", "https://centar.mk"),
        ("sportmedia", "https://sportmedia.mk"),
        ("magazin", "https://magazin.mk"),
        ("smartportal", "https://smartportal.mk"),
        ("makpress", "https://makpress.mk"),
        ("a1on", "https://a1on.mk"),
        ("plusinfo", "https://plusinfo.mk"),
        ("mkd-news", "https://mkd-news.com"),
        ("mkinfo", "https://mkinfo.mk"),
        ("slobodenpecat", "https://slobodenpecat.mk"),
        ("press24", "https://press24.mk"),
        ("nezavisen", "https://nezavisen.mk"),
        ("trn", "https://trn.mk"),
        ("4news", "https://4news.mk"),
        ("racin", "https://racin.mk"),
        ("netpress", "https://netpress.com.mk"),
        ("makedonija24", "https://makedonija24.mk"),
        ("puls24", "https://puls24.mk"),
    ]

    posts_per_page: int = 100
    posts_url: str = "{site_url}/wp-json/wp/v2/posts"
    categories_url: str = "{site_url}/wp-json/wp/v2/categories"

    # Scraping settings
    max_concurrent_requests: int = 10
    request_timeout: int = 20

    # Rate limiting
    requests_per_second: float = 5

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # HTTP headers
    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    model_config = {
        "env_file": ".env"
    }


settings = ScraperSettings()