from ..base_page import BasePage
from ..router import register_route
from ..naviator import Navigator

import flet as ft

@register_route("/missav")
class MissavPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "Hanime"
        self._test_btn = ft.ElevatedButton("测试", on_click=self.test)

    def test(self, e):
        self.interact.start_spider("missav",{
            'scrape_type':'test',
        })


    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("Missav"),
                self._test_btn
            ]
        )
