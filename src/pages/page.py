import flet as ft
from typing import Dict, Type, Any, Optional, List, Callable
from interface import Requester, Subscriber
from abc import ABC, abstractmethod
from loguru import logger


# T = TypeVar('T', bound='BasePage')

# ======= 交互函数 =======
class InteractionReqSub(ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._requester = Requester()
        self._subscriber = Subscriber()
        # self._handle_message : Callable[[str,Any],Any] = None

    def request(self, data: Any, timeout: int = 5000, use_json: bool = True) -> Optional[Any]:
        return self._requester.request(data, timeout, use_json)

    def subscribe(self, topic: str):
        self._subscriber.subscribe_topic(topic)

    # def set_handler(self, hander: Callable[[str,Any],Any]):
    #     self._handle_message = hander

    @abstractmethod
    def on_subscribe(self, topic: str, data: Any):
        raise NotImplementedError

    # 监听发布
    def start_listening(self):
        self._subscriber.start_receiving(self.on_subscribe)

# ======= 基础页面类 =======
class BasePage(ABC):
    router  = None  # 全局路由器引用（单例）

    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self._build()

    @abstractmethod
    def _build(self) -> ft.Control:
        """子类实现UI构建"""
        raise NotImplementedError

    def show(self):
        """显示该页面"""
        content = self._build()
        self.page.controls.clear()
        self.page.add(content)
        self.page.update()

    def enter(self):
        """进入该页面时调用"""
        pass

    def exit(self):
        """离开该页面时调用"""
        pass


    def go(self, path: str):
        """导航到其他页面"""
        if BasePage.router:
            BasePage.router.go(path, self.page)
        else:
            raise RuntimeError("Router 未初始化")


# ======= 单例路由器（不依赖 ft.Page） =======
class Router:
    _instance = None

    def __init__(self):
        self.routes : Dict[str, Type[BasePage]] = {}      # 路径 -> 页面类
        self.instances : Dict[str, BasePage] = {}   # 路径 -> 页面实例缓存
        self.active_path : str = "/"                # 当前活动页面路径

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            BasePage.router = cls._instance
        return cls._instance

    def register(self, path: str):
        """装饰器注册页面类"""
        def decorator(cls):
            self.routes[path] = cls
            return cls
        return decorator

    def go(self, path: str, page: ft.Page):
        """页面跳转+生命周期管理"""
        if path not in self.routes:
            logger.warning(f"路由 {path} 未注册")
            return

        page_cls = self.routes[path]

        # 调用前一页面 exit()
        if self.active_path in self.instances:
            current = self.instances[self.active_path]
            if hasattr(current, "exit"):
                current.exit()

        if path not in self.instances:
            self.instances[path] = page_cls(page)

        instance = self.instances[path]
        self.active_path = path

        # 调用 enter()
        if hasattr(instance, "enter"):
            instance.enter()

        instance.show()