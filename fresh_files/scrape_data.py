from typing import List
from dataclasses import dataclass, field


LINKS = {}
CURRENT_CHANNEL = ""


@dataclass
class ContentScrapeInfo:
    _scrape_time: str = None
    links: List = field(default=list)

    @property
    def scrape_time(self) -> str:
        if self.pages > 0:
            return self._scrape_time

    @scrape_time.setter
    def scrape_time(self, dif_time):
        self._scrape_time = f"%.2f" % dif_time

    @property
    def pages(self) -> int:
        if not self.links:
            return 0

        for links in [self.links, self.links[0]]:
            if type(links) is list and len(links) > 1:
                return len(links)
        else:
            return 1
