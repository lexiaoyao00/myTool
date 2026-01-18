import flet as ft
from abc import ABC, abstractmethod
from typing import Dict
from loguru import logger

from .naviator import Navigator
from .interaction import InteractSpider



class CommonNavBar(ft.AppBar):
    def __init__(self, title: str, nav: Navigator):
        super().__init__(
            title=ft.Text(title),
            actions=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=nav.back),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=nav.forward),
            ]
        )

class CommonAllert(ft.AlertDialog):
    def __init__(self, title: str, content: str, actions: list[ft.Control] = None):
        super().__init__(
            title=ft.Text(title),
            content=ft.Text(content),
            actions= actions
        )

# 基类
class BasePage(ABC):
    def __init__(self, page: ft.Page, nav: Navigator):
        self.page = page
        self.nav = nav
        self._route = '/'
        self.interact = InteractSpider()

        self.interact.set_ws_handler(self.handle_ws_msg)

        self._status_callbacks = {
        'failed': self.on_status_failed,
        'error': self.on_status_failed,
        'running': self.on_status_running,
        'success': self.on_status_success,
        'finished': self.on_status_finished,
    }

    def common_navbar(self, title: str):
        # return ft.AppBar(
        #     title=ft.Text(title),
        #     actions=[
        #         ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.nav.back),
        #         ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.nav.forward),
        #     ]
        # )
        return CommonNavBar(title, self.nav)

    async def on_status_failed(self, msg: Dict):
        """处理任务失败"""
        self.page.open(ft.AlertDialog(title='ERROR',content=ft.Text(value=msg['message'])))


    async def on_status_running(self, msg: Dict):
        """处理任务运行中"""
        pass

    async def on_status_success(self, msg: Dict):
        """处理任务成功"""
        pass

    async def on_status_finished(self, msg: Dict):
        """处理爬虫任务结束"""
        pass

    async def handle_ws_msg(self, msg: Dict):
        """处理ws 信息的回调"""
        # pass
        status = msg.get('status')
        if status and status in self._status_callbacks:
            await self._status_callbacks[status](msg)


    async def listen_ws(self, task_id:str):
        await self.interact.listen_ws(task_id)


    @property
    def route(self) -> str:
        """页面路由路径"""
        return self._route

    @route.setter
    def route(self, value: str):
        if not value.startswith('/'):
            value = '/' + value
        self._route = value

    @abstractmethod
    def build(self) -> ft.View:
        raise NotImplementedError

