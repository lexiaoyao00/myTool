import flet as ft
from ..page import BasePage
from ..router import register_route,Navigator


@register_route("/hanime")
class HanimePage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self.page.title = "Hanime"
        self._column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls = [
                ft.Text(value="Hanime", size=30, weight=ft.FontWeight.BOLD),
                ft.Text(value="This is a preview of the Hanime page", size=20),
                ft.ElevatedButton(text='test',on_click=self.test),
            ],
        )

    def test(self,e:ft.ControlEvent):
        # e.control.disabled = True
        self.nav.navigate('/')


    def build(self) -> ft.View:
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("danbooru"),
                self._column,
            ],
        )
