from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from modules import (
    SpiderType,
    SpiderManager,
    DanbooruScraper,
    Laowang,
    HAnimeScraper,
    SSTM,
    ExHentaiScraper,
    MissavScraper)
import asyncio
from loguru import logger
from typing import List


app = FastAPI()


# WebSocket 管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_progress(self, progress_data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(progress_data)
            except:
                pass

ws_manager = ConnectionManager()
spider_manager = SpiderManager()


@app.get("/")
async def init():
    global spider_manager
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang, SpiderType.AUTOMATION)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM, SpiderType.AUTOMATION)
    spider_manager.register("exhentai", ExHentaiScraper)
    spider_manager.register("missav", MissavScraper)


    # spdiers = {
    #     '爬虫': ["danbooru", "hanime","exhentai", "missav"],
    #     '签到': ["laowang", "sstm"]
    # }

    spiders_on_page = {spider_type.value:spiders for spider_type, spiders in spider_manager.type_spiders.items()}

    # print(spiders_on_page)
    return {"status": "OK", "spiders": spiders_on_page}

@app.post("/start/{spider_name}")
def start(spider_name: str, params: dict = None):
    global spider_manager
    params = params or {}
    try:
        spider_is_running = spider_manager.is_running(spider_name)
        if spider_is_running:
            return {"status": "NG", "message": f"{spider_name} 已经在运行中"}

        task_id = spider_manager.run_spider(spider_name, **params)
        if task_id:
            return {"status": "OK", "task_id": task_id}
        return {"status": "NG", "message": f"Failed to start {spider_name}"}
    except Exception as e:
        return {"status": "ERROR","message": f"Failed to start {spider_name}: {str(e)}"}

@app.post("/stop/{spider_name}")
def stop(spider_name: str):
    global spider_manager
    spider_manager.stop(spider_name)
    return {"status": "OK", "message": f"{spider_name} 已停止"}

@app.post("/stop_all")
def stop_all():
    global spider_manager
    spider_manager.stop_all()
    return {"status": "OK", "message": "所有爬虫已停止"}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(ws: WebSocket, task_id: str):
    global spider_manager
    await ws.accept()
    q = spider_manager.task_queues.get(task_id)
    if q is None:
        logger.warning(f"任务 {task_id} 不存在")
        await ws.send_json({"status": "error", "message": f"任务 {task_id} 不存在"})
        await ws.close()
        return

    try:
        finished = False
        while not finished:
            messages = []
            for _ in range(10):  # 一次最多取10条
                if not q.empty():
                    try:
                        msg = q.get_nowait()
                        messages.append(msg)
                        if msg.get("status") in ["finished", "error"]:
                            finished = True
                    except:
                        break
                else:
                    break

            # 发送所有消息
            for msg in messages:
                await ws.send_json(msg)

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"任务 {task_id} 的客户端关闭ws连接")

    except Exception as e:
        # 连接中断也可以清理
        logger.error(f"任务 {task_id} 连接中断, 错误信息：{e}")
        await ws.send_json({"status": "error", "message": f"任务 {task_id} 连接中断"})

    finally:
        await ws.close()
        spider_manager.clean_queue(task_id)



def run_api():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_api()