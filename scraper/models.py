from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Article:
    """Represents a scraped article."""

    id: str
    title: str
    site_url: str
    page_url: str
    content: Optional[str] = None
    published_at: Optional[str] = None
    categories: List[str] = None
    metadata: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """Serialize the Article into a dictionary."""

        return {
            "id": self.id,
            "title": self.title,
            "site_url": self.site_url,
            "page_url": self.page_url,
            "content": self.content,
            "published_at": self.published_at,
            "categories": self.categories,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Article":
        """Deserialize a dictionary into an Article instance."""

        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            site_url=data.get("site_url", ""),
            page_url=data.get("page_url", ""),
            content=data.get("content"),
            published_at=data.get("published_at"),
            categories=data.get("categories"),
            metadata=data.get("metadata"),
        )
