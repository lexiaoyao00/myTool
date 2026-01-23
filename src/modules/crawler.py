from abc import ABC, abstractmethod

from queue import Queue



class Crawler(ABC):
    """爬虫基类"""
    def __init__(self, queue:Queue, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue  # 进程队列，用于传递数据

    @staticmethod
    @abstractmethod
    async def run(self, *args, **kwargs):
        ...
