import json
import logging
from pathlib import Path
from typing import Iterable, List, Dict, Any, Set

from .base_store import BaseStore
from scraper import Article

logger = logging.getLogger(__name__)


class JSONFileStore(BaseStore):
    """JSON file storage with separate files for records and IDs."""

    def __init__(self, articles_file_path: str, seen_ids_file_path: str):
        self.records_file_path = Path(articles_file_path)
        self.seen_ids_file_path = Path(seen_ids_file_path)

        self.records_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.seen_ids_file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all_articles(self) -> List[Dict[str, Any]]:
        """Load all articles from the JSON file."""

        if not self.records_file_path.exists():
            return []

        try:
            with self.records_file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("File %s is empty or corrupted. Returning empty list.", self.records_file_path)
            return []

    def save_articles(self, articles: Iterable[Article]) -> None:
        """Append new articles to the JSON file and update seen IDs."""

        articles_list = list(articles)

        if not articles_list:
            logger.info("No articles to save")
            return

        article_dicts = [record.to_dict() for record in articles_list]

        existing_articles = self.load_all_articles()
        existing_articles.extend(article_dicts)

        with self.records_file_path.open("w", encoding="utf-8") as f:
            json.dump(existing_articles, f, indent=2, ensure_ascii=False)

        logger.info("Added %d new articles (total: %d)", len(articles_list), len(existing_articles))

        new_ids = {article.id for article in articles_list}
        self.save_seen_ids(new_ids)

    def save_seen_ids(self, ids: Set[str]) -> None:
        """Append new IDs to the existing seen IDs file."""

        existing_ids = self.load_seen_ids()
        existing_ids.update(ids)

        with self.seen_ids_file_path.open("w", encoding="utf-8") as f:
            json.dump(sorted(list(existing_ids)), f, indent=2, ensure_ascii=False)

        logger.info("Added %d new seen IDs (total: %d)", len(ids), len(existing_ids))

    def load_seen_ids(self) -> Set[str]:
        """Load the set of seen article IDs from the seen IDs file."""

        if not self.seen_ids_file_path.exists():
            return set()

        try:
            with self.seen_ids_file_path.open("r", encoding="utf-8") as f:
                ids_list = json.load(f)
                logger.info("Loaded %d previously seen IDs", len(ids_list))
                return set(ids_list)

        except json.JSONDecodeError:
            logger.warning("File %s is empty or corrupted. Returning empty set.", self.seen_ids_file_path)
            return set()

    def clear(self) -> None:
        """Clear all stored article and seen IDs by deleting both files."""

        if self.records_file_path.exists():
            self.records_file_path.unlink()
            logger.info("Cleared records file: %s", self.records_file_path)

        if self.seen_ids_file_path.exists():
            self.seen_ids_file_path.unlink()
            logger.info("Cleared seen IDs file: %s", self.seen_ids_file_path)
