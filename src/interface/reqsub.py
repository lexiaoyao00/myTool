from typing import Any, Optional, Callable,Dict
from . import Requester
from . import Subscriber


class InteractionReqSub():
    def __init__(self, request_addr:str, subscribe_addr:str,  on_subscribe: Callable[[str, Any], None] = None):
        self._requester = Requester(request_addr)
        self._subscriber = Subscriber(subscribe_addr)
        self._on_subscribe = on_subscribe if on_subscribe is not None else self.default_on_subscribe

        self.start_listening()  # 启动监听

    def request(self, data: Any, timeout: int = 5000, use_json: bool = True) -> Optional[Any]:
        return self._requester.request(data, timeout, use_json)

    def subscribe(self, topic: str):
        self._subscriber.subscribe_topic(topic)

    def unsubscribe(self, topic: str):
        self._subscriber.unsubscribe_topic(topic)

    def set_subscribe_callback(self, on_subscribe: Callable[[str, Any], None]):
        self._on_subscribe = on_subscribe

    def default_on_subscribe(self, topic: str, data: Any):
        print(f"Received data from topic {topic}: {data}")

    # 监听发布
    def start_listening(self):
        self._subscriber.start_receiving(self._on_subscribe)


class ReqSubFactory():
    _instance = None
    _reqsubs : Dict[str, InteractionReqSub] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get(cls, name:str, request_addr:str, subscribe_addr:str, subscribe_handler: Callable[[str,Any],Any] = None, **kwargs):
        if cls._reqsubs and name in cls._reqsubs:
            return cls._reqsubs[name]

        cls._reqsubs[name] = InteractionReqSub(request_addr, subscribe_addr, subscribe_handler, **kwargs)
        return cls._reqsubs[name]
