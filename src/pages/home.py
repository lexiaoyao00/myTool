import flet as ft
from typing import Callable, Any
from .base_page import BasePage
from .router import register_route,Navigator
import requests

class SpiderButton(ft.ElevatedButton):
    def __init__(self, name: str, on_click: Callable[[ft.ControlEvent], Any]):
        super().__init__()
        self.text = name
        self.on_click = on_click

    def disable(self):
        self.disabled = True
        self.update()

    def enable(self):
        self.disabled = False
        self.update()



class SpiderTab(ft.Tab):
    def __init__(self, name: str):
        super().__init__()
        self._container = ft.Container(
            margin=10,
            padding=10,
            expand=True,
            alignment=ft.alignment.top_center,
            content=ft.Row()
        )

        self.text = name
        self.content = self._container

    def add_button(self, button: SpiderButton):
        self._container.content.controls.append(button)

# @Router.instance().register("/home")
@register_route("/")
class HomePage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.spiders = {}
        self.has_build = False
        self.init()

    def init(self):
        self.page.title = "Home Page"

        if not self.spiders:
            r = requests.get("http://127.0.0.1:8000/")
            self.spiders = r.json()['spiders']
        # lv = ft.ListView()
        # for spider in self.spiders:
        #     lv.controls.append(ft.Text(spider))
        # dlg = ft.AlertDialog(
        #     title=ft.Text("以添加的爬虫："),
        #     content=lv,
        #     alignment=ft.alignment.center,
        # )
        # self.page.open(dlg)
        self._tabs_name =[]
        self._tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
        )
        self._view = ft.View(route=self.route,
                        controls=[
                            self.common_navbar("首页"),
                            self._tabs
                        ]
                    )

    def add_tab(self, tab_name:str):
        if tab_name in self._tabs_name:
            self.page.open(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text(f"标签 '{tab_name}'已存在"),
                alignment=ft.alignment.center,
            ))
            return
        self._tabs_name.append(tab_name)
        self._tabs.tabs.append(SpiderTab(tab_name))

        self.page.update()


    def add_button(self, tab_name:str, text:str, on_click:Callable):
        if tab_name not in self._tabs_name:
            self.page.open(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text(f"标签 '{tab_name}' 不存在"),
                alignment=ft.alignment.center,
            ))
            return

        idx = self._tabs_name.index(tab_name)
        self._tabs.tabs[idx].add_button(SpiderButton(text, on_click))

        self.page.update()


    def start_spider(self,e:ft.ControlEvent):
        # print(e.control)
        spider = e.control.text

        r = requests.post(f"http://127.0.0.1:8000/start/{spider}")


    def navgiate(self, e:ft.ControlEvent):
        route = f"/{e.control.text}"
        self.nav.navigate(route)


    def build(self) -> ft.View:
        if self.has_build:
            return self._view

        if not isinstance(self.spiders, dict):
            self.page.open(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text(f"爬虫列表获取失败"),
                alignment=ft.alignment.center,
            ))
            return ft.View(
                route=self.route,
                controls=[
                    self.common_navbar("首页"),
                    self._tabs,
                ]
            )


        # print(self.spiders)
        for spider_tag in self.spiders.keys():
            self.add_tab(spider_tag)
            if spider_tag == "爬虫":
                for task in self.spiders[spider_tag]:
                    self.add_button(spider_tag, task, self.navgiate)
            else:
                for task in self.spiders[spider_tag]:
                    self.add_button(spider_tag, task, self.start_spider)


        # self.add_tab("爬虫")
        # # self.add_button("爬虫", "danbooru", self.start_spider)
        # self.add_button("爬虫", "danbooru", lambda e:self.nav.navigate('/danbooru'))
        # self.add_button("爬虫", "hanime", self.start_spider)
        # # self.add_button("爬虫", "test", self.start_spider)


        # self.add_tab("签到")
        # self.add_button("签到", "laowang", self.start_spider)
        # self.add_button("签到", "sstm", self.start_spider)

        self.has_build = True
        return self._view