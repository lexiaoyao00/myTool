# import multiprocessing
from typing import Dict, Type, List
from collections import defaultdict
import asyncio
from queue import Queue
from loguru import logger
from .crawler import Crawler
import uuid
import threading
from enum import StrEnum
import time

class SpiderType(StrEnum):
    """
    爬虫类型
    """
    SCRAPER = "爬虫"         # 数据爬虫
    AUTOMATION = "签到"     # 自动化爬虫

class SpiderManager():
    """
    统一的爬虫管理类：
    - 注册/取消注册爬虫函数
    - 启动/停止爬虫子进程
    - 查询运行状态
    """

    def __init__(self):
        super().__init__()
        # 保存所有已注册的爬虫{name: 入口函数}
        self._registry: Dict[str, Type[Crawler]] = {}
        self._processes : Dict[str, threading.Thread] = {}
        self.task_queues : Dict[str, Queue] = {} # 外部清理
        self.type_spiders: Dict[SpiderType, List[str]] = defaultdict(list)
        self.spider_instances: Dict[str, Crawler] = {}
        self._lock = threading.Lock()

    def __del__(self):
        self.stop_all()

    # ------- 注册相关 -------
    def register(self, name: str, target: Type[Crawler], spider_type: SpiderType = SpiderType.SCRAPER):
        """注册爬虫类"""
        if name in self._registry:
            raise ValueError(f"爬虫 {name} 已注册")

        if not issubclass(target, Crawler):
            raise TypeError("爬虫必须是 Crawler 子类")
        self._registry[name] = target
        self.type_spiders[spider_type].append(name)
        logger.info(f"已注册爬虫: {name}")

    def unregister(self, name: str):
        """取消注册爬虫（如在运行则先停止）"""
        if name not in self._registry:
            logger.warning(f"爬虫 {name} 未注册")
            return
        # 如果正在运行，先停止
        if self.is_running(name):
            self.stop(name)
        del self._registry[name]
        logger.info(f"取消注册成功: {name}")

    def list_spiders(self):
        """列出所有已注册爬虫"""
        return list(self._registry.keys())

    # ------- 运行管理 -------
    def run_spider(self, name: str, *args, **kwargs):
        with self._lock:
            if name not in self._registry:
                logger.error(f"爬虫 {name} 未注册")
                return None

            if name in self._processes and self._processes[name].is_alive():
                logger.warning(f"爬虫 {name} 已在运行")
                return None

            task_id = str(uuid.uuid4())
            instance = self.spider_instances.get(name)
            if not instance:
                q = Queue()
                instance = self._registry[name](queue=q)
                self.spider_instances[name] = instance
            self.task_queues[task_id] = instance.queue

            t = threading.Thread(target=self._run, args=(instance, *args), kwargs=kwargs, daemon=True)
            t.start()
            self._processes[name] = t

        # 启动监控线程（不需要锁）
        threading.Thread(target=self._monitor_process, args=(name, task_id), daemon=True).start()
        return task_id

    def _monitor_process(self, name, task_id):
        p = self._processes.get(name)
        if not p:
            logger.warning(f"监控线程：未找到爬虫 {name}")
            return

        # 先等待线程结束（join 在锁外）
        p.join()   # 只阻塞这个后台线程, 不会影响 UI

        # join 后进行清理 —— 这是修改共享字典的地方
        with self._lock:
            self.clean_queue(task_id)
            self._processes.pop(name, None)

        logger.info(f"爬虫 {name} 已结束")



    def clean_queue(self, task_id):
        """ 清理队列 """
        q = self.task_queues.pop(task_id, None)
        if q:
            logger.info(f"队列 {task_id} 已清理")

    def stop(self, name: str):
        """停止单个爬虫进程"""
        p = self._processes .get(name)
        if p and p.is_alive():
            p.terminate()   # 发信号
        else:
            logger.info(f"爬虫 {name} 不在运行或已结束")

    def stop_all(self):
        """停止所有正在运行的爬虫"""
        for name in list(self._processes .keys()):
            self.stop(name)

    def is_running(self, name: str) -> bool:
        """检查爬虫是否在运行"""
        p = self._processes .get(name)
        return p.is_alive() if p else False

    def _run(self,instance:Crawler, *args, **kwargs):
        """子线程运行爬虫"""
        logger.info(f"[子线程] 启动")

        instance.queue.put({"status": "start"})
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(instance.run(*args, **kwargs))
            loop.close()
        except Exception as e:
            logger.error(f"[子线程] 异常: {e}")
            instance.queue.put({"status": "error", "message": str(e)})
        finally:
            instance.queue.put({"status": "finished"})
            logger.info("[子线程] 任务完成")