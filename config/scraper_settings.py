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
        ("irl.mk", "https://irl.mk"),
        ("infomax.mk", "https://infomax.mk"),
        ("kurir.mk", "https://kurir.mk"),
        ("republika.mk", "https://republika.mk"),
        ("centar.mk", "https://centar.mk"),
        ("sportmedia.mk", "https://sportmedia.mk"),
        ("magazin.mk", "https://magazin.mk"),
        ("smartportal.mk", "https://smartportal.mk"),
        ("makpress.mk", "https://makpress.mk"),
        ("a1on.mk", "https://a1on.mk"),
        ("plusinfo.mk", "https://plusinfo.mk"),
        ("mkd-news.com", "https://mkd-news.com"),
        ("mkinfo.mk", "https://mkinfo.mk"),
        ("slobodenpecat.mk", "https://slobodenpecat.mk"),
        ("press24.mk", "https://press24.mk"),
        ("nezavisen.mk", "https://nezavisen.mk"),
        ("trn.mk", "https://trn.mk"),
        ("4news.mk", "https://4news.mk"),
        ("racin.mk", "https://racin.mk"),
        ("netpress.com.mk", "https://netpress.com.mk"),
        ("makedonija24.mk", "https://makedonija24.mk"),
        ("puls24.mk", "https://puls24.mk"),
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