import logging
from typing import Iterable, List, Set, Dict, Any
from abc import ABC, abstractmethod

from scraper import Article

logger = logging.getLogger(__name__)


class BaseStore(ABC):
    """Abstract base class for persisting scraped records."""

    @abstractmethod
    def load_all_articles(self) -> List[Dict[str, Any]]:
        """Load all existing articles from the store."""
        pass

    @abstractmethod
    def save_articles(self, articles: Iterable[Article]) -> None:
        """Save a collection of scraped articles to the store."""
        pass

    @abstractmethod
    def load_seen_ids(self) -> Set[str]:
        """Load the set of article IDs that have already been processed."""
        pass

    @abstractmethod
    def save_seen_ids(self, ids: Set[str]) -> None:
        """Save the set of seen article IDs to the store."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored articles."""
        pass
