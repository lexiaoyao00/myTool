import flet as ft




class DanbooruPreview(ft.UserControl):
    def __init__(self, post):
        super().__init__()
        self.post = post
        self.image = ft.Image(
            src=post.file_url,
            width=400,
            height=400,
            fit=ft.ImageFit.COVER,
            border_radius=10,
        )
        self.text = ft.Text(
            value=post.tags,
            color=ft.colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=20,
        )
        self.column = ft.Column(
            [
                self.image,
                self.text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )