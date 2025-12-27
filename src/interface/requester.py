import zmq
from typing import Any,Optional
from loguru import logger

from .base import ZMQBase


class Requester(ZMQBase):
    """请求者类（客户端）"""

    def __init__(self, address: str = "tcp://localhost:5556"):
        """
        初始化请求者
        :param address: 服务器地址
        """
        super().__init__()
        self.address = address
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.address)
        self.is_running = True
        logger.info(f"Requester connected to {address}")

    def request(self, data: Any, timeout: int = 5000, use_json: bool = True) -> Optional[Any]:
        """
        发送请求并等待响应
        :param data: 请求数据
        :param timeout: 超时时间（毫秒）
        :param use_json: 是否使用JSON序列化
        :return: 响应数据
        """
        if not self.is_running:
            raise RuntimeError("Requester is closed")

        # 设置超时
        self.socket.setsockopt(zmq.SNDTIMEO, timeout)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            # 发送请求
            if use_json:
                self.socket.send_json(data)
            else:
                self.socket.send_string(str(data))
            logger.debug(f"Request sent: {data}")

            # 接收响应
            if use_json:
                return self.socket.recv_json()
            else:
                return self.socket.recv_string()

        except zmq.Again:
            logger.error(f"Request timeout after {timeout}ms")
            # 重新创建socket以清理状态
            self._recreate_socket()
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            self._recreate_socket()
            return None

    def request_raw(self, data: bytes, timeout: int = 5000) -> Optional[bytes]:
        """
        发送原始字节请求
        :param data: 请求数据（字节）
        :param timeout: 超时时间（毫秒）
        :return: 响应数据（字节）
        """
        if not self.is_running:
            raise RuntimeError("Requester is closed")

        self.socket.setsockopt(zmq.SNDTIMEO, timeout)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            self.socket.send(data)
            logger.debug(f"Request raw sent: {data}")
            return self.socket.recv()
        except zmq.Again:
            logger.error(f"Request timeout after {timeout}ms")
            self._recreate_socket()
            return None

    def _recreate_socket(self):
        """重新创建socket（用于错误恢复）"""
        self.socket.close()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.address)

    def close(self):
        """关闭请求者"""
        with self._lock:
            if self.is_running:
                self.is_running = False
                self.socket.close()
                self.context.term()
                logger.info("Requester closed")
