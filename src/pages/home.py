import flet as ft
from interface import Publisher
from typing import Callable, Any
from core.utils import TopicName,CommandType
from .page import BasePage,Router,InteractionReqSub

@Router.instance().register("/home")
class HomePage(BasePage,InteractionReqSub):
    def __init__(self, page: ft.Page):
        super().__init__(page=page)
        self.init()
        # self.event_publisher = Publisher()
        # self.event_reqSub = InteractionReqSub()

    def init(self):
        self.page.title = "Home Page"
        self.start_listening()


    def on_subscribe(self, topic: str, data: Any):
        print(f"Received message on topic {topic}: {data}")


    def _build(self):
        request_data = {
            "type": CommandType.START.value,
            "topic": TopicName.SPIDER.value,
            "params": {
                "start_page": 1,
            }
        }
        danbooru_msg = f"danbooru {request_data}"
        laowang_msg = f"laowang {request_data}"
        scrape_container = ft.Container(
            margin=10,
            padding=10,
            expand=True,
            alignment=ft.alignment.top_center,
            content=ft.Row([
                ft.ElevatedButton(
                    text="danbooru",
                    on_click=lambda e:self.request(danbooru_msg),
                ),
                ft.ElevatedButton(
                    text="hanime",
                    on_click=lambda e:self.request("hanime"),
                ),

            ])
        )
        login_container = ft.Container(
            margin=10,
            padding=10,
            expand=True,
            alignment=ft.alignment.top_center,
            content=ft.Row([
                ft.ElevatedButton(
                    text="laowang",
                    on_click=lambda e:self.request(laowang_msg),
                ),
                ft.ElevatedButton(
                    text="sstm",
                    on_click=lambda e:self.request("sstm"),
                ),

            ])
        )

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
            tabs=[
                ft.Tab(
                    text="爬虫",
                    content=scrape_container
                ),
                ft.Tab(
                    text="签到",
                    content=login_container
                ),
            ],
        )

        return tabs
