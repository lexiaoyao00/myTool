import flet as ft
from ..page import BasePage
from ..router import register_route,Navigator
import requests

from curl_cffi import AsyncSession

@register_route("/danbooru")
class DanbooruPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "Danbooru"
        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls = [
                ft.Text(value="Danbooru", size=30, weight=ft.FontWeight.BOLD),
                ft.Text(value="This is a preview of the Danbooru page", size=20),
                ft.ElevatedButton(text='test',on_click=self.test),
            ],
        )

    async def test(self,e:ft.ControlEvent):
        # e.control.disabled = True
        # self.nav.navigate('/')
        r = requests.post(f"http://127.0.0.1:8000/start/danbooru", json={'scrape_type':'page'})
        print(r.json())
        res_json = r.json()
        if res_json['status'] == 'OK':
            # self.nav.navigate('/danbooru/preview')
            # e.control.disabled = True
            print(res_json['task_id'])
            # self.page.update()
            await self.listen_ws(res_json['task_id'])


    async def listen_ws(self,task_id):
        async with AsyncSession() as session:
            ws = await session.ws_connect(f"ws://127.0.0.1:8000/ws/{task_id}")
            await ws.flush()
            async for msg in ws:
                print("=========ws recv=========")
                print(msg.decode("utf-8"))

            # data = await ws.recv_json()
            # print("=========ws recv=========")
            # print(data)




    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("danbooru"),
                self._column,
            ],
        )



class DanbooruPreview(ft.Container):
    def __init__(self, post):
        super().__init__()
        self.post = post
        self.image = ft.Image(
            src=post.file_url,
            width=400,
            height=400,
            fit=ft.ImageFit.COVER,
            border_radius=10,
        )
        self.text = ft.Text(
            value=post.tags,
            color=ft.colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=20,
        )
        self.column = ft.Column(
            [
                self.image,
                self.text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )