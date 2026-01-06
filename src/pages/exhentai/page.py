import flet as ft
from ..page import BasePage
from ..router import register_route,Navigator
import requests
from curl_cffi import AsyncSession
from typing import Callable, List, Dict


@register_route("/exhentai")
class ExhentaiPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "ExHentai"

        self.init()



    def init(self):
        self._page_url = ft.TextField(label="Page Url")
        self._post_url = ft.TextField(label="Post Url")
        self._saw_url = ft.TextField(label="Saw Url")
        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            controls = [
                self._page_url,
                self._post_url,
                self._saw_url,
                ft.ElevatedButton(text='page',on_click=self.test_page),
                ft.ElevatedButton(text='post',on_click=self.test_post),
                ft.ElevatedButton(text='saw',on_click=self.test_saw),
                ft.ElevatedButton(text='metadata',on_click=self.test_metadata),
            ],
        )

    async def test_saw(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/exhentai", json={
            'scrape_type':'saw',
            'url': self._saw_url.value
            })


    async def test_metadata(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/exhentai", json={
            'scrape_type':'metadata',
            })

    async def test_page(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/exhentai", json={
            'scrape_type':'page',
            'url': self._page_url.value
            })

    async def test_post(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/exhentai", json={
            'scrape_type':'post',
            'url': self._post_url.value
            })
        # print(r.json())

        # await self.listen_ws(r.json()['task_id'])


    async def search(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/hanime", json={'scrape_type':'search'})
        print(r.json())

        await self.listen_ws(r.json()['task_id'])


    async def listen_ws(self,task_id):
        async with AsyncSession() as session:
            ws = await session.ws_connect(f"ws://127.0.0.1:8000/ws/{task_id}")

            try:
                while True:
                    msg:Dict = await ws.recv_json()
                    status:str|None = msg.get('status')

                    # if status == "success":
                    print("=========ws recv=========")
                    print(msg)

                    if status == 'finished':
                        print("=========ws recv finished=========")
                        break

                    if msg is None:
                        print("链接关闭")
                        break

                        # self._preview_gallery.extent(data['data'])
                        # self.page.update()
            except Exception as e:
                # logger.error(f'ws 接收消息时发生错误:{e}')
                print(f'ws 接收消息时发生错误:{e}')
            # data = await ws.recv_json()
            # print("=========ws recv=========")
            # print(data)
            await ws.close()

    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("exhentai"),
                self._column,
            ],
        )
