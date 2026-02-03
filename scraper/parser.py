import logging
from typing import Any, List, Dict, Optional
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory, LangDetectException

from .models import Article

DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class Parser:
    """Class for parsing scraped data."""

    def __init__(self, site_url: str, site_name: str):
        self.site_url = site_url
        self.site_name = site_name

    def parse(self, raw_posts: List[Dict[str, Any]], metadata: Dict) -> List[Article]:
        """Parse a list of WordPress article dictionaries into structured Article objects."""

        articles = []
        category_map = metadata.get('category_map', {})

        for post_dict in raw_posts:
            try:
                article = self.parse_post(post_dict, category_map)
                if article is not None:
                    articles.append(article)
            except Exception as e:
                logger.error("Error parsing post %s: %s", post_dict.get("url"), e)
                continue

        return articles

    def parse_post(self, post_dict: Dict[str, Any], category_map: Dict[int, str]) -> Optional[Article]:
        """Parse a single WordPress post dictionary into a structured Article."""

        post_id = post_dict.get("id")
        title = post_dict.get("title", {}).get("rendered", "")
        page_url = post_dict.get("link")
        content = self._strip_html(post_dict.get("content", {}).get("rendered", ""))
        published_at = post_dict.get("date")

        # if self._is_english(f"{title} {content}"):
        #     return None

        category_ids = post_dict.get("categories", [])
        categories = [category_map.get(c_id, f"category_{c_id}") for c_id in category_ids]

        article_id = f"{self.site_name}_{post_id}"

        return Article(
            id=article_id,
            title=title,
            site_url=self.site_url,
            page_url=page_url,
            content=content,
            published_at=published_at,
            categories=categories,
        )

    def _strip_html(self, raw_html: str) -> str:
        """Convert HTML content into plain text by removing tags and normalizing whitespace."""

        if not raw_html:
            return ""

        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        return " ".join(text.split())

    def _is_english(self, text: str) -> bool:
        """Check if the given text is written in English."""

        if not text or text.strip() == "":
            return False

        try:
            lang = detect(text)
            return lang == "en"
        except LangDetectException:
            return False
