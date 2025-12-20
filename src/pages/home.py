import flet as ft
from interface import Publisher

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Home Page"
        self.event_publisher = Publisher()

    def on_click_test(self, e):
        print("btn on click")


    def show(self):
        scrape_container = ft.Container(
            margin=10,
            padding=10,
            content=ft.Row([
                ft.ElevatedButton(
                    text="danbooru",
                    on_click=None,      #TODO
                ),
                ft.ElevatedButton(
                    text="hanime",
                    on_click=None,      #TODO
                ),
            ]),
            alignment=ft.alignment.top_center
        )
        login_container = ft.Container(
            margin=10,
            padding=10,
            content=ft.Row([
                ft.ElevatedButton(
                    text="laowang",
                    on_click=lambda e:self.event_publisher.publish("login",{"site":"laowang"})     #TODO
                ),
                ft.ElevatedButton(
                    text="sstm",
                    on_click=lambda e:self.event_publisher.publish("login",{"site":"sstm"})      #TODO
                ),
            ]),
            alignment=ft.alignment.top_center
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

        self.page.add(tabs)
