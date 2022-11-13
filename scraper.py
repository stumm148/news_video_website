import os
from time import perf_counter
from typing import List, Callable
import asyncio

from scrape_data import ContentScrapeInfo
from log import log_msg

from channels_scrapers import lnk_scraper, ltv_scraper, delfi_scraper, lrytas_scraper


# new scrapers should be added only once only here
SCRAPERS_DICT = {'lnk': lnk_scraper, 'ltv': ltv_scraper,
                 'delfi': delfi_scraper, 'lrytas': lrytas_scraper}


class BaseScraper:
    """Running and controlling passed scrapers."""

    def __init__(self, scraper: Callable,
                 content_links: list,
                 channel: str = None,
                 scrape_storage=ContentScrapeInfo):

        self.scraper = scraper
        self._content_links = content_links
        self.channel = channel
        self.scrape_storage = scrape_storage()  # initiate dataclass

    @staticmethod
    def _unique(m3u8_links: list) -> list:
        """Remove doubles from scraped links."""

        unique = []
        for x in m3u8_links:
            if x and x not in unique:
                unique.append(x)
        return unique

    async def _async_main(self, content_links: list) -> List[dict]:
        """Starting scraping async all channel links"""

        tasks = []
        m3u8_links = []

        for url in content_links:
            # initiate scraper
            s = self.scraper(channel=self.channel)
            task = asyncio.create_task(s.scrape(url))
            if task not in tasks:
                tasks.append(task)
            m3u8_links = m3u8_links + await asyncio.gather(*tasks)
        return self._unique(m3u8_links)

    @property
    def run(self) -> ContentScrapeInfo:
        """Starting point to initiate scraping async."""

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # for windows
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # saving data to the dataclass
        start_time = perf_counter()
        self.scrape_storage.links = asyncio.run(self._async_main(self._content_links))
        self.scrape_storage.scrape_time = perf_counter() - start_time

        log_msg(f'''{self.channel} Scraping time: {self.scrape_storage.scrape_time} 
                 seconds {self.scrape_storage.pages} pages.''')
        return self.scrape_storage


def create_scraper(channel: str) -> Callable:
    return SCRAPERS_DICT[channel].Scraper
