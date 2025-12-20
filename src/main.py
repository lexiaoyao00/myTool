from pages import HomePage
import flet as ft
from interface import Subscriber
from typing import Dict



def subscribe():
    sub = Subscriber()
    # 定义回调函数
    def on_message(topic:str, data:Dict):
        message = data.get("data")
        if topic == "login" and message:
            print(f"Received - Topic: {topic}, Site: {message["site"]}")


    # 订阅主题
    sub.subscribe("login", on_message)

    sub.start_listening()

def main(page:ft.Page):
    home_page = HomePage(page)
    home_page.show()
    subscribe()

if __name__ == '__main__':

    ft.app(target=main)