from pages import HomePage
import flet as ft
from interface import Subscriber
from typing import Dict,Any
from loguru import logger
from core.utils import TopicName,CommandType
from modules import testDanbooruPage, test_laowang, testHAnime, testSSTM
from spiderManager import SpiderManager,InteractionResPub
from pages.page import InteractionReqSub


def subscribe():
    spider_manager = SpiderManager()
    spider_manager.register("danbooru", testDanbooruPage)
    spider_manager.register("laowang", test_laowang)
    spider_manager.register("hanime", testHAnime)
    spider_manager.register("sstm", testSSTM)


    spider_manager.start_listening()


def main(page:ft.Page):
    log_dir = 'storage/logs'
    # logger.remove()
    logger.add(f"{log_dir}/debug.log", rotation="10 MB", retention="10 days",level="DEBUG")
    logger.add(f"{log_dir}/info.log", rotation="10 MB", retention="10 days",level="INFO")
    logger.add(f"{log_dir}/warning.log", rotation="10 MB", retention="10 days",level="WARNING")
    logger.add(f"{log_dir}/error.log", rotation="10 MB", retention="10 days",level="ERROR")
    home_page = HomePage(page)
    home_page.show()
    subscribe()

if __name__ == '__main__':

    ft.app(target=main)