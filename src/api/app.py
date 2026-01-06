from fastapi import FastAPI,WebSocket
from modules import (
    SpiderManager,
    DanbooruScraper,
    Laowang,
    HAnimeScraper,
    SSTM,
    ExHentaiScraper)
import asyncio
from loguru import logger

app = FastAPI()


spider_manager = SpiderManager()


@app.get("/")
async def init():
    global spider_manager
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM)
    spider_manager.register("exhentai", ExHentaiScraper)

    spdiers = {
        '爬虫': ["danbooru", "hanime","exhentai"],
        '签到': ["laowang", "sstm"]
    }

    return {"status": "OK", "spiders": spdiers}

@app.post("/start/{spider_name}")
def start(spider_name: str, params: dict = None):
    global spider_manager
    params = params or {}
    try:
        task_id = spider_manager.run_spider(spider_name, **params)
        if task_id:
            return {"status": "OK", "task_id": task_id}
        return {"status": "NG", "message": f"Failed to start {spider_name}"}
    except Exception as e:
        return {"status": "ERROR","message": f"Failed to start {spider_name}: {str(e)}"}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(ws: WebSocket, task_id: str):
    global spider_manager
    await ws.accept()
    q = spider_manager.task_queues.get(task_id)
    if q is None:
        logger.warning(f"任务 {task_id} 不存在")
        await ws.send_text("任务不存在或已结束")
        await ws.close()
        return

    try:
        while True:
            while not q.empty():
                msg = q.get()
                await ws.send_json(msg)
                if msg.get("status") == "finished":
                    # 任务结束，清理队列
                    logger.info(f"任务 {task_id} 结束")
                    spider_manager.task_queues.pop(task_id, None)
                    # await ws.close()
                    return


            await asyncio.sleep(0.1)
    except Exception:
        # 连接中断也可以清理
        logger.error(f"任务 {task_id} 连接中断")
        if task_id in spider_manager.task_queues:
            spider_manager.task_queues.pop(task_id, None)


def run_api():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_api()