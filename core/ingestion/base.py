from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published: datetime
    raw_text: str = ""

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> list[NewsItem]:
        pass
