import curl_cffi
from curl_cffi import AsyncSession
from typing import Dict,List,Callable,Any,Awaitable

import asyncio
import inspect
from loguru import logger


class InteractSpider:
    def __init__(self):
        self._host = 'http://127.0.0.1:8000'
        self._ws_host =  'ws://127.0.0.1:8000'
        self._ws_stop_flag : Dict[str, bool] = {}


    def start_spider(self, name:str,json_data:Dict):
        url = f'{self._host}/start/{name}'
        return curl_cffi.post(url,json=json_data).json()

    def stop_listen_ws(self, task_id:str):
        if self._ws_stop_flag.get(task_id):
            self._ws_stop_flag[task_id] = True


    def set_ws_handler(self, handler:Callable[[Dict],Awaitable[Any]]):
        if not inspect.iscoroutinefunction(handler):
            raise TypeError("handler 必须是一个异步函数 (async def)")
        self._handle_ws_msg = handler

    async def _handle_ws_msg(self, msg:Dict):
        pass

    async def listen_ws(self, task_id:str):
        logger.info(f"task '{task_id}' WebSocket start")
        self._ws_stop_flag[task_id] = False
        async with AsyncSession() as session:
            ws = await session.ws_connect(f"{self._ws_host}/ws/{task_id}")
            if ws.recv_json() is None:
                logger.error(f"task '{task_id}' WebSocket 连接失败")

                msg = {
                    "status": "error",
                    "message": "WebSocket 连接失败"
                }
                await self._handle_ws_msg(msg)
                return

            try:
                while True:
                    if self._ws_stop_flag.get(task_id):
                        logger.info(f"task '{task_id}' WebSocket 停止")
                        break

                    msg:Dict = await ws.recv_json()
                    status:str = msg.get('status','')

                    if status == 'finished':
                        logger.info(f"task '{task_id}' finished")
                        break

                    if msg is None or ws.closed:
                        logger.info(f"task '{task_id}' 链接关闭")
                        break

                    await self._handle_ws_msg(msg)

            except Exception as e:
                logger.error(f'ws 接收消息时发生错误:{e}')


            logger.debug(f"task '{task_id}' WebSocket 正在关闭")
            if not ws.closed:
                await ws.close()
            logger.debug(f"task '{task_id}' WebSocket 已经关闭")
            # self._ws_stop_flag[task_id] = False
            del self._ws_stop_flag[task_id]
