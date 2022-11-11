from typing import List, Optional
import aiohttp
from abstract import AbstractScraper
import exceptions
import scrape_data


class Scraper(AbstractScraper):

    def __init__(self):
        self.channel = __name__.split('_')[0]

    def status_handler(self, url: str, status: int) -> bool:
        if status > 200:
            exceptions.error_log(url=url, channel=__name__, error=f"resp code:{status}")
            return False
        return True

    @exceptions.parse_error(__name__)
    def _parse_resp(self, url: str, data: Optional, parse_type: str = None) -> Optional:
        if parse_type == "content_id":
            return data["components"][0]["component"]["videoInfo"]["id"]
        elif parse_type == "m3u8":
            href = ''
            title = ''
            if 'videoInfo' in data:
                if 'videoUrl' in data['videoInfo']:
                    href = data['videoInfo']['videoUrl']
                if 'airDate' in data['videoInfo']:
                    if 'T' in data['videoInfo']['airDate']:
                        video_date = data['videoInfo']['airDate'].split('T')[0]
                        title = f"{data['videoInfo']['title']} - {video_date}"

            return {'title': title, 'm3u8_link': href}

    @exceptions.client_error(__name__)
    async def _get_m3u8(self, content_id: str) -> Optional[List[dict]]:
        m3u8_url_list = []
        url = f"https://lnk.lt/api/video/video-config/{content_id}"
        if url in scrape_data.LINKS[self.channel]:
            m3u8_url_list.append(scrape_data.LINKS[self.channel][url])
            return m3u8_url_list

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if not self.status_handler(url=url, status=resp.status):
                    return
                resp_json = await resp.json()
                temp_dict = self._parse_resp(url=url, data=resp_json, parse_type='m3u8')
                m3u8_url_list.append(temp_dict)
                scrape_data.LINKS[self.channel][url] = temp_dict
        return m3u8_url_list

    @exceptions.client_error(__name__)
    async def scrape(self, url: str) -> Optional[list]:
        url = f"https://lnk.lt/api/main/content-page-by-program/{url.split('/')[-1]}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if not self.status_handler(url=url, status=resp.status):
                    return
                resp_json = await resp.json()
                content_id = self._parse_resp(url=url, data=resp_json, parse_type='content_id')
                return await self._get_m3u8(content_id)
