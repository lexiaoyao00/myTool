from loguru import logger
from typing import Dict,Callable
import asyncio
import inspect
from multiprocessing import Process


class SpiderManager:
    def __init__(self):
        self.spiders : Dict[str, Callable] = {}      # 存储爬虫信息
        self.process_map : Dict[str, Process] = {}  # 存储每个爬虫当前进程

    def register_spider(self, name: str, func: Callable):
        """注册爬虫函数，自动检测是否是协程"""
        if not callable(func):
            raise TypeError("爬虫函数必须是可调用对象")
        is_async = inspect.iscoroutinefunction(func)
        self.spiders[name] = {
            "func": func,
            "is_async": is_async
        }
        logger.debug(f"已注册爬虫: {name} (协程: {is_async})")

    def run_spider(self, name: str, *args, **kwargs):
        """运行指定爬虫（同名一次只能运行一个）"""
        if name not in self.spiders:
            logger.warning(f"未找到爬虫: {name}")
            return

        # 检查是否已有运行中的同名爬虫
        if name in self.process_map:
            proc = self.process_map[name]
            if proc.is_alive():
                logger.warning(f"爬虫 '{name}' 正在运行，等待它结束后才能启动新的实例。")
                return
            else:
                # 已经结束的进程，清理记录
                del self.process_map[name]

        spider_info = self.spiders[name]
        func = spider_info["func"]
        is_async = spider_info["is_async"]

        p = Process(target=self._run, args=(func, is_async, args, kwargs))
        p.start()
        self.process_map[name] = p
        logger.info(f"爬虫 '{name}' 已启动，PID={p.pid}")

    def force_stop_spider(self, name: str):
        """强制停止指定爬虫"""
        if name in self.process_map:
            proc = self.process_map[name]
            if proc.is_alive():
                logger.warning(f"强制结束爬虫 '{name}' (PID={proc.pid})")
                proc.terminate()
                proc.join()  # 等待进程结束
                del self.process_map[name]
            else:
                logger.info(f"爬虫 '{name}' 已结束。")
                del self.process_map[name]
        else:
            logger.info(f"爬虫 '{name}' 当前未运行。")

    @staticmethod
    def _run(func, is_async, args, kwargs):
        """子进程运行爬虫"""
        import os
        logger.info(f"[子进程] PID={os.getpid()} 启动")
        if is_async:
            asyncio.run(func(*args, **kwargs))
        else:
            func(*args, **kwargs)
        logger.info(f"[子进程] PID={os.getpid()} 任务完成")
