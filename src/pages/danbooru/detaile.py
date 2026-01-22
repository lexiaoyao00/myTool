import flet as ft
from typing import Dict, Type
from ..base_page import BasePage
from ..router import register_route,Navigator
from core.utils import judge_file_type,FileType
from string import Template
import json
from pathlib import Path
from core.config import Config,ConfigManager
from core.spider import Spider
# from modules import danbooru_header
from . import download_path,data_path

from loguru import logger

import requests


@register_route('/danbooru/post')
class DanbooruDetailPage(BasePage):
    def __init__(self,page: ft.Page, nav: Navigator):
        super().__init__(page, nav)
        self._view = ft.View(
            route= self.route,
            controls=[
                self.common_navbar('Danbooru Detail'),
            ],
            )

        self.sidebar_expanded = True

        self._download_dir = download_path or 'storage/download'
        self._download_dir =  Path(self._download_dir).resolve() / 'danbooru'
        self._item_info_save_path = data_path or 'storage/data'
        self._item_info_save_path = Path(self._item_info_save_path).resolve() / 'danbooru' / 'item_info.json'
        self._item_info:Dict = None

    def toggle_sidebar(self,e):
        self.sidebar_expanded = not self.sidebar_expanded
        # self._side_bar.width = 200 if self.sidebar_expanded else 0
        self._side_bar.visible = self.sidebar_expanded

        self._toggle_button.icon = ft.Icons.CHEVRON_LEFT if self.sidebar_expanded else ft.Icons.CHEVRON_RIGHT
        self.page.update()

    async def on_status_success(self, msg):
        # return await super().on_status_success(msg)
        if msg.get('type') == 'download':
            save_path = msg.get('save_path')
            self.page.open(
                ft.SnackBar(
                    ft.Text(value=f'下载完成,保存路径:{save_path}')
                )
            )

    async def on_status_failed(self, msg):
        # return await super().on_status_failed(msg)
        if msg.get('type') == 'download':
            self.page.open(
                ft.AlertDialog(
                    title=ft.Text(value='ERROR'),
                    content=ft.Text(value='下载失败'),
                )
            )

    async def _download(self,e):
        item_info = self._item_info
        if item_info is None:
            logger.error('下载失败,未获取到item_info')
            return

        # logger.debug(f'获取到下载内容:{item_info}')
        donwload_path = Path(self._download_dir) / f'{item_info["id"]}.{item_info["file_type"]}'

        json_data = {
            "scrape_type": "download",
            "download_path" : str(donwload_path),
            "download_url" : item_info['download_url'],
        }

        res_json : Dict= self.interact.start_spider('danbooru',json_data)
        if res_json.get('status') != 'OK':
            self.page.open(
                ft.AlertDialog(
                    title=ft.Text(value='ERROR'),
                    content=ft.Text(value=res_json.get('message')),
                )
            )

        self.page.open(
            ft.SnackBar(
                ft.Text(value='开始下载')
            )
        )
        await self.listen_ws(res_json.get('task_id'))


        # 保存信息到本地
        item_info_save_path = Path(self._item_info_save_path)
        item_info_save_path.parent.mkdir(parents=True,exist_ok=True)
        item_save_info = {}
        if item_info_save_path.exists():
            with open(item_info_save_path,'r') as f:
                item_save_info = json.load(f)

        if str(item_info['id']) in item_save_info:
            logger.info('文件信息已经保存,跳过保存')
            return

        item_save_info[str(item_info['id'])] = item_info
        with open(item_info_save_path,'w') as f:
            json.dump(item_save_info,f,indent=4)



    def build(self):
        item_info = self.page.session.get('danbooru_post')
        if item_info is None:
            logger.warning('未获取到item_info')
            return self._view
        self._item_info = item_info

        t_str = Template('$name : $value')

        self._txt_id = ft.Text(value=t_str.substitute(name='ID',value=item_info.get('id','Unknown')))
        self._txt_size = ft.Text(value=t_str.substitute(name='大小',value=item_info.get('size','Unknown')))
        self._txt_file_type = ft.Text(value=t_str.substitute(name='类型',value=item_info.get('file_type','Unknown')))
        self._txt_score = ft.Text(value=t_str.substitute(name='分数',value=item_info.get('score','Unknown')))
        self._txt_resolution = ft.Text(value=t_str.substitute(name='分辨率',value=item_info.get('resolution','Unknown')))

        post_url = item_info.get('post_url')
        file_ulr = item_info.get('file_url')
        file_type = judge_file_type(file_ulr)
        if file_type == FileType.IMAGE:
            self._media = ft.Image(src=file_ulr,expand=True)
        elif file_type == FileType.VIDEO:
            self._media = ft.Video(playlist=[ft.VideoMedia(file_ulr)])

        else:
            self._media = ft.Text(value='未知类型，无法展示')
        self._btn_orginal = ft.ElevatedButton(text="访问帖子网址", on_click= lambda _: self.page.launch_url(post_url))
        self._btn_download = ft.ElevatedButton(text="下载", on_click= self._download)


        artist_tags = item_info.get('artist_tags',[])
        copyrights_tags = item_info.get('copyrights_tags',[])
        characters_tags = item_info.get('characters_tags',[])
        general_tags = item_info.get('general_tags',[])
        meta_tags = item_info.get('meta_tags',[])

        tags = artist_tags + copyrights_tags + characters_tags + general_tags + meta_tags
        tags_str = ','.join(tags)

        self._tf_tags = ft.TextField(value=tags_str, label='Tags',multiline=True, min_lines=5,read_only=True)


        self._toggle_button  = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT if self.sidebar_expanded else ft.Icons.CHEVRON_RIGHT,
            on_click=self.toggle_sidebar,
            tooltip="折叠/展开侧栏"
        )

        self._side_bar = ft.Container(
            padding=10,
            visible=self.sidebar_expanded,
            content=ft.Column([
                self._txt_id,
                self._txt_size,
                self._txt_file_type,
                self._txt_score,
                self._txt_resolution,
                self._btn_orginal,
                self._btn_download,
                self._tf_tags,
            ])
        )
        self._main_content = ft.Container(
            content=self._media,
            expand=True,
        )

        self._view.controls.clear()
        self._view.controls.extend([
            self.common_navbar('Danbooru Detail'),
            self._toggle_button,
            ft.Row([
                self._side_bar,
                self._main_content,
            ],expand=True),
        ])

        return self._view