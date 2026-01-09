import flet as ft
from ..page import BasePage
from ..router import register_route,Navigator
import requests
from functools import partial

from typing import Dict
from curl_cffi import AsyncSession


@register_route("/hanime")
class HanimePage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "Hanime"
        self._search_url_tf = ft.TextField(label="search url")
        self._watch_url_tf = ft.TextField(label="watch url")
        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            controls = [
                # ft.Text(value="Hanime", size=30, weight=ft.FontWeight.BOLD),
                # ft.Text(value="This is a preview of the Hanime page", size=20),
                self._search_url_tf,
                self._watch_url_tf,
                ft.ElevatedButton(text='test',on_click=self.test),
                ft.ElevatedButton(text='search',on_click=partial(self.on_btn_click, scrape_type='search')),
                ft.ElevatedButton(text='watch',on_click=partial(self.on_btn_click, scrape_type='watch')),
                ft.ElevatedButton(text='series',on_click=partial(self.on_btn_click, scrape_type='series')),
            ],
        )

    async def on_btn_click(self,e:ft.ControlEvent, scrape_type:str):
        # e.control.disabled = True
        # self.nav.navigate('/')
        if scrape_type == 'search':
            url = self._search_url_tf.value
        elif scrape_type in ['watch','series']:
            url = self._watch_url_tf.value
        else:
            url = None

        print(f"on_btn_click scrape_type:{scrape_type}, url:{url}")
        r = requests.post(f"http://127.0.0.1:8000/start/hanime", json={
            'scrape_type':scrape_type,
            'url':url,
            })
        print(r.json())

        await self.listen_ws(r.json()['task_id'])

    async def test(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/hanime", json={'scrape_type':'test'})
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
                self.common_navbar("hanime"),
                self._column,
            ],
        )
