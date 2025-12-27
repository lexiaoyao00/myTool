import zmq
import json
import threading
from typing import Callable, Optional, List
from loguru import logger

from .base import ZMQBase

class Subscriber(ZMQBase):
    """订阅者类"""

    def __init__(self, address: str = "tcp://localhost:5555", topics: List[str] = None):
        """
        初始化订阅者
        :param address: 连接地址
        :param topics: 要订阅的主题列表，None表示订阅所有
        """
        super().__init__()
        self.address = address
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.address)

        # 设置订阅主题
        if topics is None:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        else:
            for topic in topics:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

        self.is_running = True
        self._receive_thread = None
        self._callback = None
        logger.info(f"Subscriber connected to {address}")

    def subscribe_topic(self, topic: str):
        """
        订阅新主题
        :param topic: 主题
        """
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        logger.debug(f"Subscribed to topic {topic}")

    def unsubscribe_topic(self, topic: str):
        """
        取消订阅主题
        :param topic: 主题
        """
        self.socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)
        logger.debug(f"Unsubscribed from topic {topic}")

    def receive(self, timeout: int = None, use_json: bool = True) -> Optional[tuple]:
        """
        接收一条消息（阻塞）
        :param timeout: 超时时间（毫秒）
        :param use_json: 是否使用JSON反序列化
        :return: (topic, data) 或 None
        """
        if not self.is_running:
            return None

        if timeout:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            message = self.socket.recv_string()
            parts = message.split(" ", 1)

            if len(parts) == 2:
                topic, data = parts
                if use_json:
                    data = json.loads(data)
                return topic, data
            return parts[0], None

        except zmq.Again:
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return None

    def receive_raw(self, timeout: int = None) -> Optional[List[bytes]]:
        """
        接收原始字节消息
        :param timeout: 超时时间（毫秒）
        :return: [topic, data] 或 None
        """
        if not self.is_running:
            return None

        if timeout:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            return self.socket.recv_multipart()
        except zmq.Again:
            return None

    def start_receiving(self, callback: Callable, use_json: bool = True):
        """
        启动异步接收（在新线程中）
        :param callback: 回调函数，签名: callback(topic, data)
        :param use_json: 是否使用JSON反序列化
        """
        self._callback = callback
        self._receive_thread = threading.Thread(
            target=self._receive_loop,
            args=(use_json,),
            daemon=True
        )
        self._receive_thread.start()

    def _receive_loop(self, use_json: bool):
        """接收循环"""
        while self.is_running:
            result = self.receive(timeout=1000, use_json=use_json)
            if result and self._callback:
                topic, data = result
                logger.debug(f"Subscriber received: {result}")
                try:
                    self._callback(topic, data)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

    def stop_receiving(self):
        """停止异步接收"""
        self.is_running = False
        if self._receive_thread:
            self._receive_thread.join(timeout=2)

    def close(self):
        """关闭订阅者"""
        self.stop_receiving()
        with self._lock:
            self.socket.close()
            self.context.term()
            logger.info("Subscriber closed")
