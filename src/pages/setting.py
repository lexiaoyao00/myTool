import flet as ft
from typing import Dict, Any
from .base_page import BasePage
from .router import register_route,Navigator
from core.setting import Setting


@register_route("/settings")
class SettingPage(BasePage):
    def __init__(self, page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self._path_setting = Setting().get_config('path')
        self._save_btn = ft.ElevatedButton("保存", on_click=self._on_save_click)
        self._download_path_tf = ft.TextField(label="下载路径")
        self._data_path_tf = ft.TextField(label="数据路径")

        self._path_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Text("目录配置"),
                self._download_path_tf,
                self._data_path_tf,
            ]
        )

    def _on_save_click(self, e):
        self._path_setting.set('download_path', self._download_path_tf.value)
        self._path_setting.set('data_path', self._data_path_tf.value)
        self._path_setting.save()


    def build(self) -> ft.View:
        self._download_path_tf.value=self._path_setting.get('download_path')
        self._data_path_tf.value=self._path_setting.get('data_path')
        return ft.View(
            route=self.route,
            controls=[
                self.common_navbar("设置", show_setting_btn=False),
                self._path_column,
                self._save_btn,
            ]
        )