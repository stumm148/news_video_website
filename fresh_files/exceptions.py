from typing import Optional
import aiohttp
import asyncio
from log import log_msg
from string import Template


client_templ = Template("""scrape $error $error_info.
                           'Please, check the content link in the config file.
                           'It may no longer exist.""")

parse_templ = Template("""scrape $error $error_info.
                           'Please, check the content link in the config file.
                           'It may no longer exist or html changed.""")


def client_error(channel: str):
    def wrapper(func: Optional) -> Optional:
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except aiohttp.ClientError as error:
                error_log(channel, client_templ.substitute(error='aiohttp ClientError', error_info=error))
            except aiohttp.http.HttpProcessingError as error:
                error_log(channel, client_templ.substitute(error='aiohttp http.HttpProcessingError', error_info=error))
            except asyncio.TimeoutError as error:
                error_log(channel, client_templ.substitute(error='asyncio TimeoutError', error_info=error))
            except Exception as error:
                error_log(channel, client_templ.substitute(error='Exception', error_info=error))

        return inner
    return wrapper


def parse_error(channel: str):
    def wrapper(func: Optional) -> Optional:
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (KeyError, ValueError) as e:
                msg = parse_templ.substitute(error='KeyError or ValueError', error_info=e)
                error_log(channel=channel, error=msg)
            except Exception as e:
                msg = parse_templ.substitute(error='Exception', error_info=e)
                error_log(channel=channel, error=msg)
        return inner
    return wrapper


def error_log(channel: str, error: Optional, url: str = None) -> None:
    log_msg(f"{url} <> {channel} get error {error}.")
