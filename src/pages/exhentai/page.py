import flet as ft
from ..base_page import BasePage
from ..router import register_route,Navigator
import requests
from typing import Callable, List, Dict
from functools import partial


@register_route("/exhentai")
class ExhentaiPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)

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
                ft.ElevatedButton(text='page',on_click=partial(self.start_scrape,scrape_type='page',url=self._page_url.value)),
                ft.ElevatedButton(text='post',on_click=partial(self.start_scrape,scrape_type='post',url=self._post_url.value)),
                ft.ElevatedButton(text='saw',on_click=partial(self.start_scrape,scrape_type='saw',url=self._saw_url.value)),
                ft.ElevatedButton(text='metadata',on_click=partial(self.start_scrape,scrape_type='metadata')),
            ],
        )

    async def start_scrape(self,e:ft.ControlEvent, scrape_type:str, url:str=None):
        res_json = self.interact.start_spider(name='exhentai', json_data={
            'scrape_type':scrape_type,
            'url':url
        })

        if res_json.get('status'):
            if res_json.get('status') in ['NG','ERROR']:
                self.page.open(ft.AlertDialog(
                    title='Error',
                    content=ft.Text(res_json.get('message')),
                ))


    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("exhentai"),
                self._column,
            ],
        )
