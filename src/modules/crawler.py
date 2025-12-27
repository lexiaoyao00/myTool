from abc import ABC, abstractmethod



class Crawler(ABC):
    """爬虫基类"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    async def run(self, *args, **kwargs):
        ...
