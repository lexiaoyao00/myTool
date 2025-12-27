import zmq
import threading
from typing import Any, Callable
from loguru import logger


from .base import ZMQBase



class Responder(ZMQBase):
    """响应者类（服务器）"""

    def __init__(self, address: str = "tcp://*:5556"):
        """
        初始化响应者
        :param address: 绑定地址
        """
        super().__init__()
        self.address = address
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.address)
        self.is_running = True
        self._handler = None
        self._server_thread = None
        logger.info(f"Responder bound to {address}")

    def set_handler(self, handler: Callable[[Any], Any]):
        """
        设置请求处理函数
        :param handler: 处理函数，签名: handler(request_data) -> response_data
        """
        self._handler = handler

    def start(self, handler: Callable[[Any], Any] = None, use_json: bool = True):
        """
        启动服务器（在新线程中）
        :param handler: 请求处理函数
        :param use_json: 是否使用JSON序列化
        """
        if handler:
            self._handler = handler

        if not self._handler:
            raise ValueError("Handler not set")

        self._server_thread = threading.Thread(
            target=self._serve_loop,
            args=(use_json,),
            daemon=True
        )
        self._server_thread.start()
        logger.info("Responder started")

    def _serve_loop(self, use_json: bool):
        """服务循环"""
        while self.is_running:
            try:
                # 设置接收超时，以便能够检查is_running
                self.socket.setsockopt(zmq.RCVTIMEO, 1000)

                # 接收请求
                if use_json:
                    request = self.socket.recv_json()
                else:
                    request = self.socket.recv_string()

                logger.debug(f"Responder received request: {request}")
                # 处理请求
                try:
                    response = self._handler(request)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
                    response = {"error": str(e)}

                # 发送响应
                if use_json:
                    self.socket.send_json(response)
                else:
                    self.socket.send_string(str(response))

            except zmq.Again:
                continue
            except Exception as e:
                if self.is_running:
                    logger.error(f"Server error: {e}")

    def serve_once(self, timeout: int = None, use_json: bool = True) -> bool:
        """
        处理一个请求（阻塞）
        :param timeout: 超时时间（毫秒）
        :param use_json: 是否使用JSON序列化
        :return: 是否成功处理
        """
        if not self._handler:
            raise ValueError("Handler not set")

        if timeout:
            self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        try:
            # 接收请求
            if use_json:
                request = self.socket.recv_json()
            else:
                request = self.socket.recv_string()

            # 处理请求
            response = self._handler(request)

            # 发送响应
            if use_json:
                self.socket.send_json(response)
            else:
                self.socket.send_string(str(response))

            return True

        except zmq.Again:
            return False
        except Exception as e:
            logger.error(f"Serve once error: {e}")
            return False

    def stop(self):
        """停止服务器"""
        self.is_running = False
        if self._server_thread:
            self._server_thread.join(timeout=2)

    def close(self):
        """关闭响应者"""
        self.stop()
        with self._lock:
            self.socket.close()
            self.context.term()
            logger.info("Responder closed")
