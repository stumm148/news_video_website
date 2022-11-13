from typing import List, Dict, Optional
import aiohttp
import lxml.html
from abstract import AbstractScraper
import exceptions
import scrape_data


class Scraper(AbstractScraper):

    def status_handler(self, url: str, status: int) -> bool:
        if status > 200:
            exceptions.error_log(url=url, channel=__name__, error=f"resp code:{status}")
            return False
        return True

    @exceptions.parse_error(__name__)
    def _parse_resp(self, url: str, data: Optional, parse_type: str = None) -> Optional:
        if parse_type == "content_url":
            html_elems = lxml.html.fromstring(data.encode('utf8'))
            content_urls = html_elems.xpath('//a[@class="media-block__link"]/@href')
            return content_urls
        elif parse_type == "m3u8":
            title = ''
            href = ''
            if 'playlist_item' in data:
                if 'file' in data['playlist_item']:
                    href = data['playlist_item']['file']
                if 'title' in data['playlist_item']:
                    title = data['playlist_item']['title']
            return {'title': title, 'm3u8_link': href}

    @staticmethod
    @exceptions.parse_error(__name__)
    def _parse_m3u8_link(all_series_url: list) -> Dict[str, str]:
        m3u8_links_dict = {}
        for url in all_series_url:
            temp_list = url.split('/')
            if len(temp_list) > 4:
                m3u8_link = f"https://www.lrt.lt/servisai/stream_url/vod/media_info/?url=%2Fmediateka%2Firasas%2F" \
                            f"{temp_list[3]}%2F{temp_list[4]}"
                m3u8_links_dict[temp_list[4]] = m3u8_link
        return m3u8_links_dict

    @exceptions.client_error(__name__)
    async def _get_m3u8(self, content_urls: list) -> Optional[List[dict]]:
        m3u8_url_list = []
        m3u8_dict = self._parse_m3u8_link(content_urls)
        for m3u8_link in m3u8_dict.values():
            if m3u8_link in scrape_data.LINKS[self.channel]:
                m3u8_url_list.append(scrape_data.LINKS[self.channel][m3u8_link])
                continue
            async with aiohttp.ClientSession() as session:
                async with session.get(m3u8_link) as resp:
                    if not self.status_handler(url=m3u8_link, status=resp.status):
                        return
                    resp_json = await resp.json()
                    temp_dict = self._parse_resp(url=m3u8_link, data=resp_json, parse_type='m3u8')
                    m3u8_url_list.append(temp_dict)
                    scrape_data.LINKS[self.channel][m3u8_link] = temp_dict
        return m3u8_url_list

    @exceptions.client_error(__name__)
    async def scrape(self, url: str) -> Optional[List[Dict[str, str]]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if not self.status_handler(url=url, status=resp.status):
                    return
                body = await resp.text()
                content_urls = self._parse_resp(url=url, data=body, parse_type='content_url')
                m3u8_url_list = await self._get_m3u8(content_urls)
                return m3u8_url_list
