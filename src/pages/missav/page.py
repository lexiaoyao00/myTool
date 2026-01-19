from ..base_page import BasePage
from ..router import register_route
from ..naviator import Navigator
from core.config import PRO_DIR
from pathlib import Path
import json
from typing import Dict, Any
import flet as ft

@register_route("/missav")
class MissavPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "MissAv"
        self._search_tf = ft.TextField(label="搜索", value='mide-565')
        self._test_btn = ft.ElevatedButton("测试", on_click=self.test)

    async def test(self, e):
        search_query = self._search_tf.value
        json_data = {
            'scrape_type':'search',
            'query':search_query
        }
        res_json = self.interact.start_spider("missav", json_data)
        if res_json['status'] in ['NG','ERROR']:
            self.page.open(ft.AlertDialog(content=ft.Text(value=res_json['message'])))
            return

        await self.listen_ws(res_json['task_id'])


    async def on_status_success(self, msg:Dict):
        # print(msg)
        save_path = PRO_DIR / 'storage/data/missav' / 'search.json'
        save_path.parent.mkdir(parents=True, exist_ok=True)

        search_item_list = msg.get('data', [])
        if not search_item_list:
            self.page.open(ft.AlertDialog(content=ft.Text(value='未找到相关数据')))
            return

        # item = search_item_list[0]

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=4)

    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("Missav"),
                self._search_tf,
                self._test_btn
            ]
        )
