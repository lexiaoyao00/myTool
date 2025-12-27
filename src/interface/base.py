import zmq
import json
import threading
import time
from typing import Any, Callable, Optional, Dict, List
from abc import ABC, abstractmethod


class ZMQBase(ABC):
    """ZMQ基类"""

    def __init__(self):
        self.context = zmq.Context()
        self.socket = None
        self.is_running = False
        self._lock = threading.Lock()

    @abstractmethod
    def close(self):
        """关闭连接"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

