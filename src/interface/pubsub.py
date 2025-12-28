from typing import Any, Callable, Optional

from .publisher import Publisher
from .subscriber import Subscriber


class InteractionPubSub():
    def __init__(self, publish_addr:str, subscrib_addr:str, subscribe_handler: Callable[[str,Any],Any] = None, **kwargs):
        super().__init__(**kwargs)
        self._publisher = Publisher(publish_addr)
        self._subscriber = Subscriber(subscrib_addr)
        # self._handle_message : Callable[[str,Any],Any] = None
        self.on_subscribe : Callable[[str,Any],Any] = subscribe_handler if subscribe_handler else self.default_on_subscribe

    def publish(self, topic: str, data: Any, use_json: bool = True):
        self._publisher.publish(topic, data, use_json)

    def subscribe(self, topic: str):
        self._subscriber.subscribe_topic(topic)


    def default_on_subscribe(self, topic: str, data: Any):
        print(f"topic:{topic}, data:{data}")
    # def set_handler(self, hander: Callable[[str,Any],Any]):
    #     self._handle_message = hander
    def set_subscribe_handler(self, hander: Callable[[str,Any],Any]):
        self.on_subscribe = hander

    # 监听发布
    def start_listening(self):
        self._subscriber.start_receiving(self.on_subscribe)