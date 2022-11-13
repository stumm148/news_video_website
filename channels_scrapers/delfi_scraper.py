from typing import List, Optional, Dict
import aiohttp
import lxml.html
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
        if parse_type == "m3u8":
            html_elems = lxml.html.fromstring(data)
            elems = html_elems.xpath('//a[@class="video-title"]')
            for elem in elems:
                content_id = ''
                lead_video = ''
                title = elem.text.strip()
                if not title:
                    title_elem = elem.xpath('//em')
                    if title_elem:
                        title = title_elem[0].text.strip()
                if 'data-salt' in elem.keys():
                    content_id = elem.attrib['data-salt']
                if 'data-leadvideo' in elem.keys():
                    lead_video = elem.attrib['data-leadvideo']

                if lead_video and content_id and "dvideo" in lead_video:
                    href = f"https://vodhls.dcdn.lt/dvideo/videos/{content_id[0]}/" \
                           f"{content_id}/smil:stream.smil/playlist.m3u8"
                    temp_dict = {'title': title, 'm3u8_link': href}
                    m3u8_url_list.append(temp_dict)
        return m3u8_url_list

    @exceptions.client_error(__name__)
    async def scrape(self, url: str) -> Optional[List[Dict[str, str]]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if not self.status_handler(url=url, status=resp.status):
                    return
                body = await resp.text()
                m3u8_url_list = self._parse_resp(url=url, data=body, parse_type='m3u8')
                return m3u8_url_list
