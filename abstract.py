from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractScraper(ABC):
    """Enabling to use same method names in all scrapers."""

    @abstractmethod
    def status_handler(self, url: str, status: int) -> bool:
        pass

    @abstractmethod
    def _parse_resp(self, url: str, data: Optional, parse_type: str = None) -> Optional:
        pass

    @abstractmethod
    def scrape(self, url: str) -> Optional[List[dict]]:
        pass
