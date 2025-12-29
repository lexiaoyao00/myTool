import flet as ft
from interface import Publisher
from typing import Callable, Any
from core.utils import TopicName,CommandType
from .page import BasePage,Router
from interface.reqsub import InteractionReqSub,ReqSubFactory

class SpiderButton(ft.ElevatedButton):
    def __init__(self, name: str, on_click: Callable[[ft.ElevatedButton], Any]):
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

@Router.instance().register("/home")
class HomePage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page=page)
        self._reqsub = ReqSubFactory.get(name='ui',request_addr="tcp://localhost:5556",subscribe_addr="tcp://localhost:5555", subscribe_handler=self.on_subscribe)
        self.init()

    def init(self):
        self.page.title = "Home Page"

        self._tabs_name =[]
        self._tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
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


    def on_subscribe(self, topic: str, data: Any):
        print(f"Received message on topic {topic}: {data}")

    def _build(self):
        self.add_tab("爬虫")
        self.add_button("爬虫", "danbooru", lambda e:self._reqsub.request("danbooru"))
        self.add_button("爬虫", "hanime", lambda e:self._reqsub.request("hanime"))


        self.add_tab("签到")
        self.add_button("签到", "laowang", lambda e:self._reqsub.request("laowang"))
        self.add_button("签到", "sstm", lambda e:self._reqsub.request("sstm"))


        return self._tabs