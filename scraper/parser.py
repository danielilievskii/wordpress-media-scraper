import logging
from datetime import datetime
from typing import Any, List, Dict, Optional
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory, LangDetectException
from vezilka_schemas import Record, RecordMeta, RecordType
from html import unescape

DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class Parser:
    """Class for parsing scraped data."""

    def __init__(self, site_url: str, site_name: str):
        self.site_url = site_url
        self.site_name = site_name

    def parse(self, raw_posts: List[Dict[str, Any]], metadata: Dict) -> List[Record]:
        """Parse a list of WordPress article dictionaries into structured Article objects."""

        articles = []
        category_map = metadata.get('category_map', {})
        batch_timestamp = datetime.now()

        for post_dict in raw_posts:
            try:
                article = self.parse_post(post_dict, category_map, batch_timestamp)
                if article is not None:
                    articles.append(article)
            except Exception as e:
                logger.error("Error parsing post %s: %s", post_dict.get("url"), e)
                continue

        return articles

    def parse_post(self, post_dict: Dict[str, Any], category_map: Dict[int, str], timestamp: datetime) -> Optional[Record]:
        """Parse a single WordPress post dictionary into a structured Article."""

        id = post_dict.get("id")
        page_url = post_dict.get("link")
        title = post_dict.get("title", {}).get("rendered", "")

        html_text = post_dict.get("content", {}).get("rendered", "")
        clean_text = self._clean_html_text(html_text)

        # if self._is_english(f"{title}"):
        #     return None

        text = f"Наслов: {title}\n\n Текст: {clean_text}"

        category_ids = post_dict.get("categories", [])
        categories = [category_map.get(c_id, f"category_{c_id}") for c_id in category_ids]

        article_id = f"{self.site_name}_{id}"

        meta = RecordMeta(
            source=self.site_name,
            url=page_url,
            tags=categories,
            labels=[],
            scraped_at=timestamp,
        )

        record = Record(
            id=article_id,
            text=text,
            type=RecordType.NARRATIVE,
            last_modified_at=timestamp,
            meta=meta
        )

        return record

    def _clean_html_text(self, raw_html: str) -> str:
        """Convert HTML content into plain text by removing tags and normalizing whitespace."""

        if not raw_html:
            return ""

        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        normalized_text = " ".join(text.split())
        return unescape(normalized_text)

    def _is_english(self, text: str) -> bool:
        """Check if the given text is written in English."""

        if not text or text.strip() == "":
            return False

        try:
            lang = detect(text)
            return lang == "en"
        except LangDetectException:
            return False
