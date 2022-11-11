import ast
from flask import Flask, render_template, request
import scraper
import config_json
from log import log_msg
import scrape_data
from scrape_data import ContentScrapeInfo


app = Flask(__name__)

config = config_json.read_config('config.json')
CHANNEL_LIST = config.channel_info.keys()
scrape_data.LINKS = {channel: {} for channel in CHANNEL_LIST}


def clean_storage() -> None:
    for channel in scrape_data.LINKS.keys():
        if channel == scrape_data.CURRENT_CHANNEL:
            scrape_data.LINKS[channel].clear()
            break


def create_status_msg(content_info: ContentScrapeInfo) -> str:
    status_msg = ""
    if content_info.pages:
        status_msg = f"Async scraping {content_info.pages} pages in {content_info.scrape_time} seconds. " \
                     f"Some links can be found and added from the cache."
    return status_msg


@app.route('/')
def start_page():
    log_msg(str(CHANNEL_LIST))
    return render_template('main.html', channel_list=CHANNEL_LIST, status_msg=f"Status")


@app.route('/tv_content', methods=['POST', 'GET'])
def tv_content():
    if request.method == 'POST':
        channel = [i for i in request.form][0]
        scrape_data.CURRENT_CHANNEL = channel
        content_info = start_scrape(channel)
        status_msg = create_status_msg(content_info)
        log_msg(status_msg)
        return render_template('tv_content.html', status_msg=status_msg,
                               m3u8_url_list=content_info.links,
                               channel=channel.upper())
    return render_template('main.html', channel_list=CHANNEL_LIST, status_msg=f"Status")


@app.route('/result', methods=['POST', 'GET'])
def result():

    if request.method == 'POST':
        req_type = [i for i in request.form][0]
        if req_type == 'clean_storage':
            clean_storage()
            return render_template('main.html', channel_list=CHANNEL_LIST,
                                   status_msg=f"{scrape_data.CURRENT_CHANNEL} link storage cleaned")

        for i in request.form:
            json_elem = ast.literal_eval(i)
            log_msg(str(json_elem["m3u8_link"]))
            return render_template('Online Streaming Player For Free (HLS_M3U8_RTMP_MP4 Player).html',
                                   result_url=json_elem["m3u8_link"], result_name=json_elem["title"])

    return render_template('main.html', channel_list=CHANNEL_LIST, status_msg=f"Status")


def start_scrape(channel: str) -> ContentScrapeInfo:
    """Connecting frontend to backend(scrapers)"""

    content_links = config.content_links(channel)
    scraper_mod = scraper.create_scraper(channel=channel)
    video_content_info = scraper.BaseScraper(scraper=scraper_mod,
                                             content_links=content_links,
                                             channel=channel).run
    return video_content_info


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000)
    # app.run(host='0.0.0.0', port=int("5000"))
