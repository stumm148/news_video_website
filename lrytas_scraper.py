from typing import List, Optional, Dict
import aiohttp
from abstract import AbstractScraper
import exceptions


class Scraper(AbstractScraper):

    def status_handler(self, url: str, status: int) -> bool:
        if status > 200:
            exceptions.error_log(url=url, channel=__name__, error=f"resp code:{status}")
            return False
        return True

    @exceptions.parse_error(__name__)
    def _parse_resp(self, url: str, data: Optional, parse_type: str = None) -> Optional:
        m3u8_url_list = []
        if 'media1:' not in data:
            return m3u8_url_list

        data_list = data.split('media1:')
        if len(data_list) > 1:
            for s in data_list[1:]:
                a, b = s.find('title:'), s.find('category:')
                title = s[a + 7: b - 2]
                c, d = s.find('ssb.lrytas.lt'), s.find('.m3u8')
                href = s[c + 13: d + 5].replace("\\\\u002F", "/").replace('\/', '/')
                href = f'https://ssb.lrytas.lt{href}'
                m3u8_url_list.append({'title': title, 'm3u8_link': href})
        return m3u8_url_list

    @exceptions.client_error(__name__)
    async def scrape(self, url: str) -> Optional[List[Dict[str, str]]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if not self.status_handler(url=url, status=resp.status):
                    return
                body = await resp.text()
                m3u8_url_list = self._parse_resp(url=url, data=body)
            return m3u8_url_list
