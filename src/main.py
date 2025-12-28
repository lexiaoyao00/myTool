from pages import HomePage
import flet as ft
from loguru import logger
from modules import testDanbooruPage, test_laowang, testHAnime, testSSTM
from modules import DanbooruScraper,Laowang, HAnimeScraper, SSTM
from spiderManager import SpiderManager,SpiderManagerFunc


def subscribe_spider():
    spider_manager = SpiderManager()
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM)


    # spider_manager = SpiderManagerFunc()
    # spider_manager.register("danbooru", testDanbooruPage)
    # spider_manager.register("laowang", test_laowang)
    # spider_manager.register("hanime", testHAnime)
    # spider_manager.register("sstm", testSSTM)


    spider_manager.start_listening()


def main(page:ft.Page):
    # ConfigManager('/config/spider.toml')
    log_dir = 'storage/logs'
    logger.remove()
    logger.add(f"{log_dir}/debug.log", rotation="10 MB", retention="10 days",level="DEBUG")
    logger.add(f"{log_dir}/info.log", rotation="10 MB", retention="10 days",level="INFO")
    logger.add(f"{log_dir}/warning.log", rotation="10 MB", retention="10 days",level="WARNING")
    logger.add(f"{log_dir}/error.log", rotation="10 MB", retention="10 days",level="ERROR")
    home_page = HomePage(page)
    home_page.show()
    subscribe_spider()

if __name__ == '__main__':

    ft.app(target=main)