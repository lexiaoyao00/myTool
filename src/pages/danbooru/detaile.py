import flet as ft
from typing import Dict, Type
from ..page import BasePage
from ..router import register_route,Navigator


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
        self.init()



    def init(self):
        item_info = self.page.session.get('danbooru_post')
        if item_info is None:
            # self.page.go('/')
            self._view.controls.append(ft.Text(value='No data'))
            return

        self._txt_id = ft.Text(value=item_info.get('id','Unknown'))
        self._txt_size = ft.Text(value=item_info.get('size','Unknown'))
        self._txt_file_type = ft.Text(value=item_info.get('file_type','Unknown'))
        self._txt_score = ft.Text(value=item_info.get('score','Unknown'))
        self._txt_resolution = ft.Text(value=item_info.get('resolution','Unknown'))

        artist_tags = item_info.get('artist_tags',[])
        copyrights_tags = item_info.get('copyrights_tags',[])
        characters_tags = item_info.get('characters_tags',[])
        general_tags = item_info.get('general_tags',[])
        meta_tags = item_info.get('meta_tags',[])

        tags = artist_tags + copyrights_tags + characters_tags + general_tags + meta_tags
        tags_str = ','.join(tags)

        self._tf_tags = ft.TextField(value=tags_str, label='Tags',multiline=True, min_lines=5,read_only=True)
        # self._media = ft.Image(src='',expand=True)

    def build(self):
        item_info = self.page.session.get('danbooru_post')
        if item_info is None:
            return self._view

        self._txt_id = ft.Text(value=item_info.get('id','Unknown'))
        self._txt_size = ft.Text(value=item_info.get('size','Unknown'))
        self._txt_file_type = ft.Text(value=item_info.get('file_type','Unknown'))
        self._txt_score = ft.Text(value=item_info.get('score','Unknown'))
        self._txt_resolution = ft.Text(value=item_info.get('resolution','Unknown'))

        artist_tags = item_info.get('artist_tags',[])
        copyrights_tags = item_info.get('copyrights_tags',[])
        characters_tags = item_info.get('characters_tags',[])
        general_tags = item_info.get('general_tags',[])
        meta_tags = item_info.get('meta_tags',[])

        tags = artist_tags + copyrights_tags + characters_tags + general_tags + meta_tags
        tags_str = ','.join(tags)

        self._tf_tags = ft.TextField(value=tags_str, label='Tags',multiline=True, min_lines=5,read_only=True)


        self._view.controls.clear()
        self._view.controls.extend([
            self.common_navbar('Danbooru Detail'),
            self._txt_id,
            self._txt_size,
            self._txt_file_type,
            self._txt_score,
            self._txt_resolution,
            self._tf_tags,
        ])

        return self._view