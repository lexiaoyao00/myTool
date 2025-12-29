from typing import Any, Callable, Dict

from .publisher import Publisher
from .subscriber import Subscriber


class InteractionPubSub():
    def __init__(self, publish_addr:str, subscrib_addr:str, subscribe_handler: Callable[[str,Any],Any] = None, **kwargs):
        super().__init__(**kwargs)
        self._publisher = Publisher(publish_addr)
        self._subscriber = Subscriber(subscrib_addr)
        # self._handle_message : Callable[[str,Any],Any] = None
        self.on_subscribe : Callable[[str,Any],Any] = subscribe_handler if subscribe_handler else self.default_on_subscribe


        self.start_listening()

    def publish(self, topic: str, data: Any, use_json: bool = True):
        self._publisher.publish(topic, data, use_json)

    def subscribe(self, topic: str):
        self._subscriber.subscribe_topic(topic)

    def unsubscribe(self, topic: str):
        self._subscriber.unsubscribe_topic(topic)

    def default_on_subscribe(self, topic: str, data: Any):
        print(f"topic:{topic}, data:{data}")
    # def set_handler(self, hander: Callable[[str,Any],Any]):
    #     self._handle_message = hander
    def set_subscribe_handler(self, hander: Callable[[str,Any],Any]):
        self.on_subscribe = hander

    # 监听发布
    def start_listening(self):
        self._subscriber.start_receiving(self.on_subscribe)


class PubSubFactory():
    _instance = None
    _pubsubs : Dict[str, InteractionPubSub] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get(cls, name:str, publish_addr:str, subscrib_addr:str, subscribe_handler: Callable[[str,Any],Any] = None, **kwargs):
        if cls._pubsubs and name in cls._pubsubs:
            return cls._pubsubs[name]

        cls._pubsubs[name] = InteractionPubSub(publish_addr, subscrib_addr, subscribe_handler, **kwargs)
        return cls._pubsubs[name]
