import flet as ft

def window1(page: ft.Page):
    page.title = "窗口1"
    page.add(ft.Text("这是第一个窗口"))

def window2(page: ft.Page):
    page.title = "窗口2"
    page.add(ft.Text("这是第二个窗口"))

if __name__ == "__main__":
    # 启动两个窗口
    ft.app(target=window1)
    ft.app(target=window2)
