import multiprocessing
from typing import Callable, Dict, Any, Union, Type
import asyncio
from loguru import logger
from .crawler import Crawler
import uuid
import time
import threading

# class InteractionResPub(ABC):
#     """交互响应发布者"""
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self._responder = Responder()
#         self._publisher = Publisher()
#         # self._handle_message : Callable[[Any],Any] = None

#     # def set_handler(self, handler: Callable[[Any], Any]):
#     #     self._handle_message = handler

#     @abstractmethod
#     def handle_request(data):
#         raise NotImplementedError

#     def publish(self, topic: str, data: Any):
#         self._publisher.publish(topic, data)

#     def start_listening(self):
#         self._responder.start(self.handle_request)


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
        # 保存正在运行的爬虫进程{name: Process对象}
        self._processes: Dict[str, multiprocessing.Process] = {}
        self.task_queues = {}

        threading.Thread(target=self._cleanup_task_queues, daemon=True).start()


    def __del__(self):
        self.stop_all()

    # ------- 注册相关 -------
    def register(self, name: str, target: Type[Crawler]):
        """注册爬虫函数，自动检测是否是协程"""
        if name in self._registry:
            raise ValueError(f"爬虫 {name} 已注册")

        if not issubclass(target, Crawler):
            raise TypeError("爬虫必须是 Crawler 子类")
        self._registry[name] = target
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

        if name in self._processes and self._processes[name].is_alive():
            logger.warning(f"爬虫 {name} 已在运行")
            return None

        q = multiprocessing.Queue()
        task_id = str(uuid.uuid4())
        self.task_queues[task_id] = q
        target = self._registry[name]
        p = multiprocessing.Process(target=self._run, args=(target, q, args, kwargs),daemon=True)
        p.start()
        self._processes[name] = p
        logger.info(f"爬虫 {name} 已启动 PID={p.pid}")
        return task_id

    def _cleanup_task_queues(self):
        while True:
            time.sleep(60)  # 每分钟检查
            for task_id in list(self.task_queues.keys()):
                q = self.task_queues[task_id]
                # 这里可以加判断队列是否长期无数据，或者任务超时
                if q.empty():
                    del self.task_queues[task_id]

    def stop(self, name: str):
        """停止单个爬虫进程"""
        p = self._processes.get(name)
        if p and p.is_alive():
            p.terminate()
            p.join()
            logger.info(f"爬虫 {name} 已停止")
        self._processes.pop(name, None)

    def stop_all(self):
        """停止所有正在运行的爬虫"""
        for name in list(self._processes.keys()):
            self.stop(name)

    def is_running(self, name: str) -> bool:
        """检查爬虫是否在运行"""
        p = self._processes.get(name)
        return p.is_alive() if p else False

    @staticmethod
    def _run(target: Type[Crawler],q:multiprocessing.Queue, args, kwargs):
        """子进程运行爬虫"""
        import os
        logger.info(f"[子进程] PID={os.getpid()} 启动")
        instance = target(queue=q)
        q.put({"status":"start"})
        asyncio.run(instance.run(*args, **kwargs))
        logger.info(f"[子进程] PID={os.getpid()} 任务完成")
        q.put({"status":"finished"})


# class SpiderManagerFunc(InteractionResPub):
#     """
#     统一的爬虫管理类：
#     - 注册/取消注册爬虫函数
#     - 启动/停止爬虫子进程
#     - 查询运行状态
#     """

#     def __init__(self):
#         super().__init__()
#         # 保存所有已注册的爬虫{name: 入口函数}
#         self._registry: Dict[str, dict] = {}
#         # 保存正在运行的爬虫进程{name: Process对象}
#         self._processes: Dict[str, multiprocessing.Process] = {}

#     def __del__(self):
#         self.stop_all()

#     def handle_request(self, data:str):
#         print(f"Received response message: {data}")

#         name = data.split(" ", 1)[0]
#         message = data.split(" ", 1)[1]

#         print(f'==== name: {name} message: {message} ====')

#         self.run_spider(name)

#         self.publish(TopicName.SPIDER.value, f"data:{data}")

#     # ------- 注册相关 -------
#     def register(self, name: str, func: Callable):
#         """注册爬虫函数，自动检测是否是协程"""
#         if name in self._registry:
#             raise ValueError(f"爬虫 {name} 已注册")

#         if not callable(func):
#             raise TypeError("爬虫函数必须是可调用对象")
#         is_async = inspect.iscoroutinefunction(func)
#         self._registry[name] = {
#             "func": func,
#             "is_async": is_async
#         }
#         logger.info(f"已注册爬虫: {name} (协程: {is_async})")

#     def unregister(self, name: str):
#         """取消注册爬虫（如在运行则先停止）"""
#         if name not in self._registry:
#             logger.warning(f"爬虫 {name} 未注册")
#             return
#         # 如果正在运行，先停止
#         if self.is_running(name):
#             self.stop(name)
#         del self._registry[name]
#         logger.info(f"取消注册成功: {name}")

#     def list_spiders(self):
#         """列出所有已注册爬虫"""
#         return list(self._registry.keys())

#     # ------- 运行管理 -------
#     def run_spider(self, name: str, *args, **kwargs):
#         """
#         启动爬虫子进程
#         :param name: 爬虫名称
#         :param args: 位置参数
#         :param kwargs: 关键字参数
#         """
#         if name not in self._registry:
#             logger.error(f"爬虫 {name} 未注册")
#             return

#         if name in self._processes and self._processes[name].is_alive():
#             logger.warning(f"爬虫 {name} 已在运行")
#             return

#         # func = self._registry[name]
#         spider_info = self._registry[name]
#         func = spider_info["func"]
#         is_async = spider_info["is_async"]
#         p = multiprocessing.Process(target=self._run, args=(func, is_async, args, kwargs),daemon=True)
#         p.start()
#         self._processes[name] = p
#         logger.info(f"爬虫 {name} 已启动 PID={p.pid}")

#     def stop(self, name: str):
#         """停止单个爬虫进程"""
#         p = self._processes.get(name)
#         if p and p.is_alive():
#             p.terminate()
#             p.join()
#             logger.info(f"爬虫 {name} 已停止")
#         self._processes.pop(name, None)

#     def stop_all(self):
#         """停止所有正在运行的爬虫"""
#         for name in list(self._processes.keys()):
#             self.stop(name)

#     def is_running(self, name: str) -> bool:
#         """检查爬虫是否在运行"""
#         p = self._processes.get(name)
#         return p.is_alive() if p else False

#     @staticmethod
#     def _run(func:Callable, is_async:bool, args, kwargs):
#         """子进程运行爬虫"""
#         import os
#         logger.info(f"[子进程] PID={os.getpid()} 启动")
#         if is_async:
#             asyncio.run(func(*args, **kwargs))
#         else:
#             func(*args, **kwargs)
#         logger.info(f"[子进程] PID={os.getpid()} 任务完成")
