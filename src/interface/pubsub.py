import time
from typing import Any, Callable
from .publisher import Publisher
from .subscriber import Subscriber

class PubSubManager:
    """发布订阅管理器，同时支持发布和订阅"""

    def __init__(self, pub_address: str = None, sub_addresses: list = None):
        """
        初始化管理器

        Args:
            pub_address: 发布地址
            sub_addresses: 订阅地址列表
        """
        self.publisher = None
        self.subscribers = []

        if pub_address:
            self.publisher = Publisher(pub_address)

        if sub_addresses:
            for addr in sub_addresses:
                sub = Subscriber(addr)
                self.subscribers.append(sub)

    def _del__(self):
        """析构函数，关闭所有连接"""
        self.close()

    def publish(self, topic: str, data: Any) -> None:
        """发布消息"""
        if self.publisher:
            self.publisher.publish(topic, data)

    def subscribe(self, address: str, topic: str, callback: Callable[[str, Any], None]) -> None:
        """订阅消息"""
        # 查找或创建订阅者
        subscriber = None
        for sub in self.subscribers:
            if sub.address == address:
                subscriber = sub
                break

        if not subscriber:
            subscriber = Subscriber(address)
            self.subscribers.append(subscriber)

        subscriber.subscribe(topic, callback)
        subscriber.start_listening()

    def close(self) -> None:
        """关闭所有连接"""
        if self.publisher:
            self.publisher.close()

        for sub in self.subscribers:
            sub.close()


