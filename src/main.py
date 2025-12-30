# from pages import Router
import time
import flet as ft
from loguru import logger
from modules import testDanbooruPage, test_laowang, testHAnime, testSSTM
from modules import DanbooruScraper,Laowang, HAnimeScraper, SSTM
from modules import SpiderManager

from pages import Navigator, RouteManager
from multiprocessing import Process
import subprocess,sys

# 应用
class MyApp:
    def main(self, page: ft.Page):
        page.title = "my app"
        page.scroll = True
        # page.window.width = 400
        # page.window.height = 300

        nav = Navigator(page)

        def route_change(e: ft.RouteChangeEvent):
            page.views.clear()
            PageCls = RouteManager.get(e.route)
            if PageCls:
                page.views.append(PageCls(page, nav).build())
            else:
                page.views.append(ft.View(
                    route=e.route,
                    controls=[ft.Text(f"404: {e.route}")]
                ))
            page.update()

        page.on_route_change = route_change
        page.go("/")   # 进入首页
        nav.current = "/"  # 初始化当前路由

    def run(self):
        ft.app(target=self.main)



def subscribe_spider():
    spider_manager = SpiderManager()
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM)

    # spider_manager.run_spider()


def main():
    from api.app import run_api

    p = Process(target=run_api)
    p.start()

    # subprocess.Popen([sys.executable,'-m','src.api.app'])

    time.sleep(1)
    # ConfigManager('/config/spider.toml')
    # log_dir = 'storage/logs'
    # logger.remove()
    # logger.add(f"{log_dir}/debug.log", rotation="10 MB", retention="10 days",level="DEBUG")
    # logger.add(f"{log_dir}/info.log", rotation="10 MB", retention="10 days",level="INFO")
    # logger.add(f"{log_dir}/warning.log", rotation="10 MB", retention="10 days",level="WARNING")
    # logger.add(f"{log_dir}/error.log", rotation="10 MB", retention="10 days",level="ERROR")
    # # home_page = HomePage(page)
    # # home_page.show()
    # # Router.instance().go("/home", page)
    # subscribe_spider()
    MyApp().run()

    p.terminate()
    p.join()


if __name__ == '__main__':
    main()
    # ft.app(target=main)