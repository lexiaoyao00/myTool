import sys
import os

# 把 src 目录加到搜索路径的最前面
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from pages.base_page import BasePage, Router
import flet as ft
import asyncio

@Router.instance().register("/home")
class HomePage(BasePage):
    def _build(self):
        self.data_text = ft.Text("等待加载数据...")
        return ft.Column([
            self.data_text,
            ft.ElevatedButton("去 关于页面", on_click=lambda _: self.go("/about")),
            ft.ElevatedButton("加载数据", on_click=self.load_data)
        ])

    async def load_data(self, e):
        self.data_text.value = "加载中..."
        self.page.update()
        await asyncio.sleep(1)  # 模拟后端请求
        self.data_text.value = "后端返回的数据"
        self.page.update()


@Router.instance().register("/about")
class AboutPage(BasePage):
    def _build(self):
        return ft.Column([
            ft.Text("关于页面"),
            ft.ElevatedButton("回 首页", on_click=lambda _: self.go("/home"))

        ])


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Flet Router 单例示例"
        page.window_width = 500
        page.window_height = 300

        # 进入首页（传入 ft.Page）
        Router.instance().go("/home", page)

    ft.app(target=main, view=ft.AppView.FLET_APP)


