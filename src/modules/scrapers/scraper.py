from abc import ABC, abstractmethod



class Scraper(ABC):
    """爬虫基类"""
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    @abstractmethod
    async def run(self, *args, **kwargs):
        ...
