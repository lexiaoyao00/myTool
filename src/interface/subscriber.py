import zmq
import json
import threading
from typing import Any, Callable, Optional, Dict
from loguru import logger


class Subscriber:
    """ZMQ订阅者类"""

    def __init__(self, address: str = "tcp://127.0.0.1:5555"):
        """
        初始化订阅者

        Args:
            address: 连接地址
        """
        self.address = address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(address)
        self._running = False
        self._thread = None
        self._callbacks: Dict[str, Callable] = {}
        logger.debug(f"Subscriber connected to {address}")

    def __del__(self):
        """析构函数，关闭连接"""
        self.close()

    def subscribe(self, topic: str = "", callback: Optional[Callable[[str, Any], None]] = None) -> None:
        """
        订阅主题

        Args:
            topic: 要订阅的主题，空字符串表示订阅所有
            callback: 收到消息时的回调函数
        """
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        if callback:
            self._callbacks[topic] = callback
        logger.debug(f"Subscribed to topic: '{topic}'")

    def unsubscribe(self, topic: str) -> None:
        """取消订阅主题"""
        self.socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)
        if topic in self._callbacks:
            del self._callbacks[topic]
        logger.debug(f"Unsubscribed from topic: '{topic}'")

    def receive_once(self, timeout: int = None) -> Optional[tuple]:
        """
        接收一次消息

        Args:
            timeout: 超时时间（毫秒）

        Returns:
            (topic, data) 元组，超时返回None
        """
        if timeout:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            message = self.socket.recv_string()
            parts = message.split(' ', 1)
            if len(parts) == 2:
                topic, json_data = parts
                data = json.loads(json_data)
                return topic, data
            return parts[0], None
        except zmq.Again:
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    def start_listening(self) -> None:
        """开始异步监听消息"""
        if self._running:
            logger.info("Already listening")
            return

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.debug("Started listening for messages")

    def _listen_loop(self) -> None:
        """监听循环"""
        # 设置接收超时，以便能够检查_running标志
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)

        while self._running:
            try:
                message = self.socket.recv_string()
                parts = message.split(' ', 1)

                if len(parts) == 2:
                    topic, json_data = parts
                    data = json.loads(json_data)

                    # 查找匹配的回调函数
                    for subscribed_topic, callback in self._callbacks.items():
                        if topic.startswith(subscribed_topic):
                            try:
                                callback(topic, data)
                            except Exception as e:
                                logger.error(f"Error in callback: {e}")

            except zmq.Again:
                # 超时，继续循环
                continue
            except Exception as e:
                if self._running:
                    logger.error(f"Error in listen loop: {e}")

    def stop_listening(self) -> None:
        """停止监听"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.debug("Stopped listening")

    def close(self) -> None:
        """关闭订阅者"""
        self.stop_listening()
        self.socket.close()
        self.context.term()
        logger.debug("Subscriber closed")
