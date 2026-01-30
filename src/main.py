# from pages import Router
import time
import flet as ft
from loguru import logger

from pages import Navigator, RouteManager
from multiprocessing import Process
from core.config import PRO_DIR
log_dir = PRO_DIR / 'storage/logs'
# logger.remove()
logger.add(f"{str(log_dir)}/debug.log", enqueue=True, rotation="10 MB", retention="10 days",level="DEBUG")
logger.add(f"{str(log_dir)}/info.log", enqueue=True, rotation="10 MB", retention="10 days",level="INFO")
logger.add(f"{str(log_dir)}/warning.log", enqueue=True,rotation="10 MB", retention="10 days",level="WARNING")
logger.add(f"{str(log_dir)}/error.log", enqueue=True,rotation="10 MB", retention="10 days",level="ERROR")

# 应用
class MyApp:
    def main(self, page: ft.Page):
        page.title = "my app"
        page.scroll = ft.ScrollMode.AUTO

        nav = Navigator(page)

        self.rm = RouteManager(page, nav)
        page.on_route_change = self.rm.route_change
        page.go("/")   # 进入首页
        nav.current = "/"  # 初始化当前路由

    def run(self):
        ft.app(target=self.main)


def main():

    from api.app import run_api

    p = Process(target=run_api)
    p.start()

    time.sleep(1)
    MyApp().run()

    p.terminate()
    p.join()

def test():
    from core.setting import Setting
    my_setting = Setting()
    print(my_setting.get_config('path').get('download_path'))
    print(my_setting.get_config('path').get('data_path'))

if __name__ == '__main__':
    # test()
    main()
    # ft.app(target=main)