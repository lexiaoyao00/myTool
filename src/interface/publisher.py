import zmq
import json
from typing import Any
from datetime import datetime
from loguru import logger


class Publisher:
    """ZMQ发布者类"""

    def __init__(self, address: str = "tcp://127.0.0.1:5555"):
        """
        初始化发布者

        Args:
            address: 绑定地址，格式如 "tcp://127.0.0.1:5555"
        """
        self.address = address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(address)
        self._running = False
        logger.debug(f"Publisher bound to {address}")

    def publish(self, topic: str, data: Any) -> None:
        """
        发布消息

        Args:
            topic: 主题
            data: 要发送的数据
        """
        message = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        # 发送格式: topic + 空格 + json数据
        self.socket.send_string(f"{topic} {json.dumps(message)}")
        logger.debug(f"Published message to {topic}: {data}")

    def publish_raw(self, topic: str, data: bytes) -> None:
        """
        发布原始字节数据

        Args:
            topic: 主题
            data: 字节数据
        """
        self.socket.send_multipart([topic.encode('utf-8'), data])

    def close(self) -> None:
        """关闭发布者"""
        self._running = False
        self.socket.close()
        self.context.term()
        logger.debug("Publisher closed")