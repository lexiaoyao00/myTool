import zmq
import json
import time
from typing import Any
from loguru import logger

from .base import ZMQBase

class Publisher(ZMQBase):
    """发布者类"""

    def __init__(self, address: str = "tcp://*:5555"):
        """
        初始化发布者
        :param address: 绑定地址，默认 tcp://*:5555
        """
        super().__init__()
        self.address = address
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(self.address)
        self.is_running = True
        logger.info(f"Publisher bound to {address}")
        # 给订阅者一些时间来连接
        time.sleep(0.5)

    def publish(self, topic: str, data: Any, use_json: bool = True):
        """
        发布消息
        :param topic: 主题
        :param data: 数据
        :param use_json: 是否使用JSON序列化
        """
        with self._lock:
            if not self.is_running:
                raise RuntimeError("Publisher is closed")

            if use_json:
                message = json.dumps(data)
            else:
                message = str(data)

            # 发送格式: topic message
            self.socket.send_string(f"{topic} {message}")
            logger.debug(f"Published message to '{topic}': {message}")

    def publish_raw(self, topic: bytes, data: bytes):
        """
        发布原始字节消息
        :param topic: 主题（字节）
        :param data: 数据（字节）
        """
        with self._lock:
            if not self.is_running:
                raise RuntimeError("Publisher is closed")

            self.socket.send_multipart([topic, data])
            logger.debug(f"Published raw message to {topic}: {data}")

    def close(self):
        """关闭发布者"""
        with self._lock:
            if self.is_running:
                self.is_running = False
                self.socket.close()
                self.context.term()
                logger.info("Publisher closed")
