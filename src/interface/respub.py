
from . import Responder,Publisher
from typing import Callable, Any, Optional, List,Dict


class InteractionResPub():
    """交互响应发布者"""
    def __init__(self,publish_addr:str, respond_addr:str, handler: Callable[[Any], Any] = None):
        self._publisher = Publisher(publish_addr)
        self._responder = Responder(respond_addr)
        self._handle_message = handler if handler else self.default_handle_message

    # def set_handler(self, handler: Callable[[Any], Any]):
    #     self._handle_message = handler

    def set_handler(self, handler: Callable[[Any], Any]):
        self._handle_message = handler
        self._responder.set_handler(self._handle_message)

    def default_handle_message(data):
        return data

    def publish(self, topic: str, data: Any):
        self._publisher.publish(topic, data)

    def start_listening(self):
        self._responder.start(self._handle_message)



class ResPubFactory():
    _instance = None
    _respubs : Dict[str, InteractionResPub] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    @classmethod
    def get(cls, name:str, publish_addr:str, respond_addr:str, handler: Callable[[Any], Any] = None, **kwargs):
        if cls._respubs and name in cls._respubs:
            return cls._respubs[name]

        cls._respubs[name] = InteractionResPub(publish_addr, respond_addr, handler, **kwargs)
        return cls._respubs[name]



