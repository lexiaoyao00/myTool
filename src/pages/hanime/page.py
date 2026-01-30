import flet as ft
from ..base_page import BasePage
from ..router import register_route,Navigator
import requests
from functools import partial
import asyncio

from typing import Dict,List
from curl_cffi import AsyncSession
from loguru import logger

@register_route("/hanime")
class HanimePage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self._search_url_tf = ft.TextField(label="search url")
        self._watch_url_tf = ft.TextField(label="watch url")
        self._progress_controls:Dict[str,ft.Control] = {}
        self._progress_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10,
            auto_scroll=False,
        )
        self._download_cb = ft.Checkbox(label="抓取 watch 或 series 信息后下载", value=False)
        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            controls = [
                # ft.Text(value="Hanime", size=30, weight=ft.FontWeight.BOLD),
                # ft.Text(value="This is a preview of the Hanime page", size=20),
                self._search_url_tf,
                self._watch_url_tf,
                self._download_cb,
                ft.Row(
                    alignment = ft.MainAxisAlignment.START,
                    controls = [
                        ft.ElevatedButton(text='search',on_click=partial(self.on_btn_click, scrape_type='search')),
                        ft.ElevatedButton(text='watch',on_click=partial(self.on_btn_click, scrape_type='watch')),
                        ft.ElevatedButton(text='series',on_click=partial(self.on_btn_click, scrape_type='series')),
                    ]
                ),


                self._progress_view,
            ],
        )

    def _progress_bar_view(self, progress:Dict[str,float]):
        for name, percent in progress.items():
            self._progress_controls[f'{name}_txt'].value = f"{name}:{percent * 100:.2f}%"
            self._progress_controls[f'{name}_bar'].value = percent

        self.page.update()

    def _append_progress_bar_view(self, files:List[str]):
        self._progress_controls.clear()
        for file in files:
            self._progress_controls[f'{file}_txt'] = ft.Text(value=f"{file}:0.00%")
            self._progress_controls[f'{file}_bar'] = ft.ProgressBar(value=0,expand=True,height=20)

        self._progress_view.controls = list(self._progress_controls.values())
        self.page.update()


    async def on_btn_click(self,e:ft.ControlEvent, scrape_type:str):
        # e.control.disabled = True
        # self.nav.navigate('/')
        if scrape_type == 'search':
            url = self._search_url_tf.value
        elif scrape_type in ['watch','series']:
            url = self._watch_url_tf.value
        else:
            url = None

        json_data = {
            'scrape_type':scrape_type,
            'url':url,
            'isdownload':self._download_cb.value
        }
        res_json = self.interact.start_spider(name='hanime',json_data=json_data)
        if res_json['status'] in ['NG','ERROR']:
            self.page.open(ft.AlertDialog(
                content=ft.Text(value=res_json['message']),
                actions=[
                    ft.TextButton(text="停止爬虫", on_click=lambda e: self.interact.stop_spider('hanime')),
                ]
                ))
            return

        await self.listen_ws(res_json['task_id'])


    async def on_status_running(self, msg:Dict):
        # return await super().on_status_running(msg)
        spider_type = msg.get('type','')
        if spider_type == 'download_start':
            logger.info(f"Hanime 开始下载")
            data:List[str] = msg.get('data',[])
            self._append_progress_bar_view(data)
        elif spider_type == 'download_end':
            logger.info(f"Hanime 下载完成")
            self.page.open(ft.AlertDialog(
                title='提示',
                content=ft.Text(value=msg.get('message','下载完成'))
            ))
        elif spider_type == 'downloading':
            progress = msg.get('progress')
            if progress:
                self._progress_bar_view(progress)

    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("hanime"),
                self._column,
            ],
        )
