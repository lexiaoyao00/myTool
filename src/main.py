from pages import Router
import flet as ft
from loguru import logger
from modules import testDanbooruPage, test_laowang, testHAnime, testSSTM
from modules import DanbooruScraper,Laowang, HAnimeScraper, SSTM
from spiderManager import SpiderManager


def subscribe_spider():
    spider_manager = SpiderManager()
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM)


def main(page:ft.Page):
    # ConfigManager('/config/spider.toml')
    log_dir = 'storage/logs'
    logger.remove()
    logger.add(f"{log_dir}/debug.log", rotation="10 MB", retention="10 days",level="DEBUG")
    logger.add(f"{log_dir}/info.log", rotation="10 MB", retention="10 days",level="INFO")
    logger.add(f"{log_dir}/warning.log", rotation="10 MB", retention="10 days",level="WARNING")
    logger.add(f"{log_dir}/error.log", rotation="10 MB", retention="10 days",level="ERROR")
    # home_page = HomePage(page)
    # home_page.show()
    Router.instance().go("/home", page)
    subscribe_spider()

if __name__ == '__main__':

    ft.app(target=main)