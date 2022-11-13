from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class ScrapeConfig:
    channel_info: Dict
    log_path: str

    def content_links(self, channel: str) -> List[str]:
        return self.channel_info[channel]['content_links']


def read_config(config_file: str) -> ScrapeConfig:
    with open(config_file, 'r') as file:
        data = json.load(file)
        return ScrapeConfig(**data)
