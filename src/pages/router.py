import flet as ft
from .base_page import BasePage,CommonNavBar
from typing import Type,List,Dict
from .naviator import Navigator


# 路由管理
class RouteManager:
    _registry : Dict[str,Type[BasePage]] = {}
    @classmethod
    def register(cls, route:str, page_class:Type[BasePage]):
        if route in cls._registry:
            raise ValueError(f"Route {route} already registered")
        if not issubclass(page_class, BasePage):
            raise ValueError(f"{page_class} is not a subclass of BasePage")
        if not hasattr(page_class, 'route'):
            raise ValueError(f"{page_class} does not have a route attribute")

        cls._registry[route] = page_class
    @classmethod
    def get(cls, path: str):
        return cls._registry.get(path)

    def __init__(self, page: ft.Page, nav: Navigator):
        self.page = page
        self.nav = nav
        self.routes : Dict[str, BasePage] = {}
        for route, page_cls in self._registry.items():
            instance = page_cls(page, nav)
            instance.route = route
            self.routes[route] = instance

    def route_change(self, e: ft.RouteChangeEvent):
        self.page.views.clear()
        if e.route in self.routes:
            self.page.views.append(self.routes[e.route].build())
        else:
            self.page.views.append(ft.View(
                route=e.route,
                controls=[
                    CommonNavBar("404",self.nav),
                    ft.Text(f"404: {e.route}")
                ]
            ))
        self.page.update()

def register_route(path:str):
    def decorator(cls):
        RouteManager.register(path, cls)
        return cls
    return decorator