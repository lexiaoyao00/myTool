from ..base_page import BasePage
from ..router import register_route
from ..naviator import Navigator
from core.config import PRO_DIR
from pathlib import Path
import json
from typing import Dict, Any
import flet as ft
from loguru import logger

@register_route("/missav")
class MissavPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self._search_tf = ft.TextField(label="搜索")
        self._search_url_tf = ft.TextField(label="搜索结果网址", value='https://missav.ws/dm139/cn/tags/原始视频?sort=monthly_views&page=1')
        self._watch_url_tf = ft.TextField(label="观看网址", value='https://missav.ws/dm18/cn/svdvd-443')
        self._query_btn = ft.ElevatedButton("查询", on_click=self._on_search_btn)
        self._watch_btn = ft.ElevatedButton("观看", on_click=self._on_watch_btn)

    async def _on_search_btn(self, e):
        search_url = self._search_url_tf.value
        search_query = self._search_tf.value
        if not search_url and not search_query:
            self.page.open(ft.AlertDialog(title="警告", content=ft.Text(value='请输入搜索关键词或网址')))
            return
        json_data = {
            'scrape_type':'search',
            'url':search_url,
            'query':search_query
        }
        res_json = self.interact.start_spider("missav", json_data)
        if res_json['status'] in ['NG','ERROR']:
            self.page.open(ft.AlertDialog(content=ft.Text(value=res_json['message'])))
            return

        await self.listen_ws(res_json['task_id'])

    async def _on_watch_btn(self, e):
        watch_url = self._watch_url_tf.value
        if not watch_url:
            self.page.open(ft.AlertDialog(title="警告", content=ft.Text(value='请输入观看网址')))
            return
        json_data = {
            'scrape_type':'watch',
            'url':watch_url
        }
        res_json = self.interact.start_spider("missav", json_data)
        if res_json['status'] in ['NG','ERROR']:
            self.page.open(ft.AlertDialog(content=ft.Text(value=res_json['message'])))
            return

        await self.listen_ws(res_json['task_id'])


    async def _on_search_success(self, msg:Dict):
        save_path = PRO_DIR / 'storage/data/missav' / 'search.json'
        save_path.parent.mkdir(parents=True, exist_ok=True)

        search_item_list = msg.get('data', [])
        if not search_item_list:
            self.page.open(ft.AlertDialog(content=ft.Text(value='未找到相关数据')))
            return

        # item = search_item_list[0]

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=4)

    async def on_status_success(self, msg:Dict):
        # print(msg)
        scrape_type = msg.get('type','')
        if scrape_type == 'search':
            await self._on_search_success(msg)
        elif scrape_type == 'watch':
            logger.info(msg)
        else:
            logger.warning(f'未知类型: {scrape_type}')


    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("Missav"),
                self._search_tf,
                self._search_url_tf,
                self._watch_url_tf,
                self._query_btn,
                self._watch_btn
            ]
        )
