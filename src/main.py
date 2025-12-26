from pages import HomePage
import flet as ft
from interface import Subscriber
from typing import Dict
from loguru import logger
from core.utils import TopicName,CommandType
from modules import testDanbooruPage, test_laowang, testHAnime, testSSTM
from spiderManager import SpiderManager


def subscribe():
    spider_manager = SpiderManager()
    spider_manager.register_spider("danbooru", testDanbooruPage)
    spider_manager.register_spider("laowang", test_laowang)
    spider_manager.register_spider("hanime", testHAnime)
    spider_manager.register_spider("sstm", testSSTM)

    sub = Subscriber()
    # 定义回调函数
    def on_message(topic:str, data:Dict):
        message = data.get("data")
        if not message:
            print(f"Received empty message on topic {topic}")
            return

        cmd = message.get("cmd")
        spider = message.get("spider")
        params = message.get("params")
        params = params or {}
        print(f"Received - Topic: {topic}, data: {message}")
        if cmd == CommandType.START.value:
            print(f"Starting spider: {spider}")
            spider_manager.run_spider(spider, **params)
        elif cmd == CommandType.STOP.value:
            print(f"Stopping spider: {spider}")
            spider_manager.force_stop_spider(spider)


    # 订阅主题
    # sub.subscribe("login", on_message)
    # sub.subscribe("scrape", on_message)
    for topic in TopicName:
        sub.subscribe(topic.value, on_message)


    sub.start_listening()

def main(page:ft.Page):
    log_dir = 'storage/logs'
    logger.remove()
    logger.add(f"{log_dir}/debug.log", rotation="10 MB", retention="10 days",level="DEBUG")
    logger.add(f"{log_dir}/info.log", rotation="10 MB", retention="10 days",level="INFO")
    logger.add(f"{log_dir}/warning.log", rotation="10 MB", retention="10 days",level="WARNING")
    logger.add(f"{log_dir}/error.log", rotation="10 MB", retention="10 days",level="ERROR")
    home_page = HomePage(page)
    home_page.show()
    subscribe()

if __name__ == '__main__':

    ft.app(target=main)