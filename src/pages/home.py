import flet as ft
from interface import Publisher
from typing import Callable, Any
from core.utils import TopicName,CommandType
from .page import BasePage,Router
from interface.reqsub import InteractionReqSub,ReqSubFactory

@Router.instance().register("/home")
class HomePage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page=page)
        self._reqsub = ReqSubFactory.get(name='ui',request_addr="tcp://localhost:5556",subscribe_addr="tcp://localhost:5555", subscribe_handler=self.on_subscribe)
        self.init()
        # self.event_publisher = Publisher()
        # self.event_reqSub = InteractionReqSub()

    def init(self):
        self.page.title = "Home Page"
        self._reqsub.start_listening()

        # scrape_container = ft.Container(
        #     margin=10,
        #     padding=10,
        #     expand=True,
        #     alignment=ft.alignment.top_center,
        #     content=ft.Row()
        # )
        # login_container = ft.Container(
        #     margin=10,
        #     padding=10,
        #     expand=True,
        #     alignment=ft.alignment.top_center,
        #     content=ft.Row()
        # )
        self.tabs_name =[]
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
            # tabs=[
            #     ft.Tab(
            #         text="爬虫",
            #         content=scrape_container
            #     ),
            #     ft.Tab(
            #         text="签到",
            #         content=login_container
            #     ),
            # ],
        )

    def add_tab(self, tab_name:str):
        if tab_name in self.tabs_name:
            self.page.open(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text(f"标签 '{tab_name}'已存在"),
                alignment=ft.alignment.center,
            ))
            return
        self.tabs_name.append(tab_name)
        self.tabs.tabs.append(
            ft.Tab(
                text=tab_name,
                content=ft.Container(
                    margin=10,
                    padding=10,
                    expand=True,
                    alignment=ft.alignment.top_center,
                    content=ft.Row()
                )
            )
        )

        self.page.update()


    def add_button(self, tab_name:str, text:str, on_click:Callable):
        if tab_name not in self.tabs_name:
            self.page.open(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text(f"标签 '{tab_name}' 不存在"),
                alignment=ft.alignment.center,
            ))
            return

        idx = self.tabs_name.index(tab_name)
        self.tabs.tabs[idx].content.content.controls.append(
            ft.ElevatedButton(
                text=text,
                on_click=on_click,
            )
        )

        self.page.update()


    def on_subscribe(self, topic: str, data: Any):
        print(f"Received message on topic {topic}: {data}")


    # def _build(self):
    #     request_data = {
    #         "type": CommandType.START.value,
    #         "topic": TopicName.SPIDER.value,
    #         "params": {
    #             "start_page": 1,
    #         }
    #     }
    #     danbooru_msg = f"danbooru {request_data}"
    #     laowang_msg = f"laowang {request_data}"
    #     scrape_container = ft.Container(
    #         margin=10,
    #         padding=10,
    #         expand=True,
    #         alignment=ft.alignment.top_center,
    #         content=ft.Row([
    #             ft.ElevatedButton(
    #                 text="danbooru",
    #                 on_click=lambda e:self.request(danbooru_msg),
    #             ),
    #             ft.ElevatedButton(
    #                 text="hanime",
    #                 on_click=lambda e:self.request("hanime"),
    #             ),

    #         ])
    #     )
    #     login_container = ft.Container(
    #         margin=10,
    #         padding=10,
    #         expand=True,
    #         alignment=ft.alignment.top_center,
    #         content=ft.Row([
    #             ft.ElevatedButton(
    #                 text="laowang",
    #                 on_click=lambda e:self.request(laowang_msg),
    #             ),
    #             ft.ElevatedButton(
    #                 text="sstm",
    #                 on_click=lambda e:self.request("sstm"),
    #             ),

    #         ])
    #     )

    #     tabs = ft.Tabs(
    #         selected_index=0,
    #         animation_duration=300,
    #         expand=True,
    #         tabs=[
    #             ft.Tab(
    #                 text="爬虫",
    #                 content=scrape_container
    #             ),
    #             ft.Tab(
    #                 text="签到",
    #                 content=login_container
    #             ),
    #         ],
    #     )

    #     return tabs

    def _build(self):
        self.add_tab("爬虫")
        self.add_button("爬虫", "danbooru", lambda e:self._reqsub.request("danbooru"))
        self.add_button("爬虫", "hanime", lambda e:self._reqsub.request("hanime"))


        self.add_tab("签到")
        self.add_button("签到", "laowang", lambda e:self._reqsub.request("laowang"))
        self.add_button("签到", "sstm", lambda e:self._reqsub.request("sstm"))


        return self.tabs