import multiprocessing
from typing import Dict, Type, List
from collections import defaultdict
import asyncio
from loguru import logger
from .crawler import Crawler
import uuid
import threading
from enum import StrEnum

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
    _spider_instance: Dict[str, Crawler] = {}  # 保存爬虫实例

    def __init__(self):
        super().__init__()
        # 保存所有已注册的爬虫{name: 入口函数}
        self._registry: Dict[str, Type[Crawler]] = {}
        self._processes : Dict[str, multiprocessing.Process] = {}
        self.task_queues : Dict[str,multiprocessing.Queue] = {} # 外部清理
        self.type_spiders: Dict[SpiderType, List[str]] = defaultdict(list)

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
        """
        启动爬虫子进程
        :param name: 爬虫名称
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        if name not in self._registry:
            logger.error(f"爬虫 {name} 未注册")
            return None

        if name in self._processes  and self._processes [name].is_alive():
            logger.warning(f"爬虫 {name} 已在运行")
            return None

        q = multiprocessing.Queue()
        task_id = str(uuid.uuid4())
        self.task_queues[task_id] = q
        target = self._registry[name]
        p = multiprocessing.Process(target=SpiderManager._run, args=(name, target, q, *args), kwargs=kwargs, daemon=True)
        p.start()
        self._processes [name] = p
        logger.info(f"爬虫 {name} 已启动 PID={p.pid}")

        # 异步监控进程，结束后自动清理
        threading.Thread(target=self._monitor_process, args=(name, task_id), daemon=True).start()
        return task_id

    def _monitor_process(self, name, task_id):
        """ 后台线程监控子进程状态，完成后清理 """
        p = self._processes [name]
        if p:
            p.join()  # 等待子进程退出
            self._processes.pop(name, None)         # 清理进程记录

        logger.info(f"爬虫 {name} 已结束")


    def clean_queue(self, task_id):
        """ 清理队列 """
        q = self.task_queues.pop(task_id, None)
        if q:
            q.close()
            q.join_thread()
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

    @staticmethod
    def _run(name: str, target: Type[Crawler], q:multiprocessing.Queue, *args, **kwargs):
        """子进程运行爬虫"""
        import os
        logger.info(f"[子进程] PID={os.getpid()} 启动")
        instance = SpiderManager._spider_instance.get(name)
        if not instance:
            instance = target(queue=q)
            SpiderManager._spider_instance[name] = instance

        q.put({"status":"start"})
        try:
            asyncio.run(instance.run(*args, **kwargs))
        except Exception as e:
            logger.error(f"[子进程] PID={os.getpid()} 发生异常: {e}")
            q.put({"status":"error", "message": str(e)})
        finally:
            logger.info(f"[子进程] PID={os.getpid()} 任务完成")
            q.put({"status":"finished"})