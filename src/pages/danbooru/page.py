import flet as ft
from ..page import BasePage
from ..router import register_route,Navigator
import requests
from typing import List,Dict
from loguru import logger
import json

from curl_cffi import AsyncSession
from core.config import ConfigManager , Config


class PreviewImage(ft.Image):
    def __init__(self, src:str):
        super().__init__(src=src)
        self.width = 180
        self.height = 180
        self.fit = ft.ImageFit.NONE
# 预览画廊
class PreviewGallery(ft.GridView):
    def __init__(self, runs_count:int = 5):
        super().__init__()
        self.runs_count = runs_count
        self.expand = True
        self.spacing = 5
        self.run_spacing = 5
        self.max_extent = 180


    def extent(self, imgs:List[str]):
        self.controls = [PreviewImage(src=img) for img in imgs]
        # self.update()

    def clean(self):
        return super().clean()


@register_route("/danbooru")
class DanbooruPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "Danbooru"
        self.page.scroll = ft.ScrollMode.AUTO

        self.init()

    def init(self):
        config_manager = ConfigManager()
        self._config : Config = config_manager.getConfig('config/spider.toml')['danbooru']

        self._post_page_url = ft.TextField(label=" 页面URL ",expand=True)
        self._page_url_row = ft.Row(controls=[
            self._post_page_url,
            ft.ElevatedButton(text="hot", on_click=self._on_url_btn_click),
            ft.ElevatedButton(text="popular", on_click=self._on_url_btn_click),
        ])


        self._start_page = ft.TextField(label=" 开始页 ",
                                        value=str(1),
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        expand=True)
        self._scrape_page_count = ft.TextField(label=" 爬取页数 ",
                                            value=str(1),
                                            keyboard_type=ft.KeyboardType.NUMBER,
                                            expand=True)

        self._submit_btn = ft.ElevatedButton(text="开始爬取", on_click=self._on_submit_btn_click)

        self._preview_gallery = PreviewGallery(runs_count=5)

        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            controls = [
                self._page_url_row,
                self._start_page,
                self._scrape_page_count,
                self._submit_btn,
            ],
        )

    def _on_url_btn_click(self,e:ft.ControlEvent):
        btn_txt:str = e.control.text

        url = self._config[btn_txt.lower()]
        self._post_page_url.value = url
        self.page.update()

    async def _on_submit_btn_click(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        self._preview_gallery.clean()
        r = requests.post(f"http://127.0.0.1:8000/start/danbooru", json={
            'scrape_type':'page',
            'url':self._post_page_url.value,
            'start_page':int(self._start_page.value),
            'scrape_page_count':int(self._scrape_page_count.value),
            })
        res_json = r.json()
        if res_json['status'] == 'OK':
            logger.info(f'start danbooru task success, task_id:{res_json["task_id"]}')
            # self.nav.navigate('/danbooru/preview')
            # e.control.disabled = True
            # print(res_json['task_id'])
            # self.page.update()
            await self.listen_ws(res_json['task_id'])


    async def listen_ws(self,task_id):
        async with AsyncSession() as session:
            ws = await session.ws_connect(f"ws://127.0.0.1:8000/ws/{task_id}")
            # await ws.flush()
            # async for msg in ws:
            #     print("=========ws recv=========")
            #     msg_json = json.loads(msg)
            #     print(msg_json)

            try:
                while True:
                    msg:Dict = await ws.recv_json()
                    status:str|None = msg.get('status')

                    if status is None:
                        print("=========ws recv=========")
                        print(msg)
                        self._preview_gallery.extent(list(msg.values()))
                        self.page.update()

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
                self.common_navbar("danbooru"),
                self._column,
                self._preview_gallery,
            ],
        )
