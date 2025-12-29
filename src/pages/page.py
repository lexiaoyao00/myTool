import flet as ft
from typing import Dict, Type, Any, Optional, List, Callable,Deque
from interface import Requester, Subscriber
from abc import ABC, abstractmethod
from loguru import logger
from collections import deque

from .router import Navigator



# 基类
class BasePage:
    def __init__(self, page: ft.Page, nav: Navigator):
        self.page = page
        self.nav = nav

    def common_navbar(self, title: str):
        return ft.AppBar(
            title=ft.Text(title),
            actions=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.nav.back),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.nav.forward),
            ]
        )

    def build(self) -> ft.View:
        raise NotImplementedError


# class Router:
#     """全局路由注册器"""
#     def __init__(self, page: ft.Page):
#         self.page = page
#         self.routes: dict[str, Callable[[], ft.View]] = {}
#         self.page.on_route_change = self._route_change

#     def route(self, path: str):
#         """装饰器注册路由"""
#         def decorator(func_or_class):
#             self.routes[path] = func_or_class
#             return func_or_class
#         return decorator

#     def go(self, path: str):
#         self.page.go(path)

#     def _route_change(self, e: ft.RouteChangeEvent):
#         self.page.views.clear()
#         constructor = self.routes.get(self.page.route)

#         if constructor is None:
#             # 404 页面
#             view = ft.View("/404", controls=[ft.Text("404 页面不存在")])
#         else:
#             # 如果是类，先实例化
#             if isinstance(constructor, type):
#                 view = constructor(self.page)
#             else:
#                 view = constructor()
#         self.page.views.append(view)
#         self.page.update()