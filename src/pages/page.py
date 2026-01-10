import flet as ft
from abc import ABC, abstractmethod

from .naviator import Navigator



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

    def common_navbar(self, title: str):
        # return ft.AppBar(
        #     title=ft.Text(title),
        #     actions=[
        #         ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.nav.back),
        #         ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.nav.forward),
        #     ]
        # )
        return CommonNavBar(title, self.nav)

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

