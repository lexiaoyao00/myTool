from fastapi import FastAPI
from modules import SpiderManager, DanbooruScraper, Laowang, HAnimeScraper, SSTM

app = FastAPI()


spider_manager = SpiderManager()


@app.get("/")
async def init():
    # global spider_manager
    # spider_manager.register("danbooru", DanbooruScraper)
    # spider_manager.register("laowang", Laowang)
    # spider_manager.register("hanime", HAnimeScraper)
    # spider_manager.register("sstm", SSTM)

    spdiers = {
        'scraper': ["danbooru", "hanime"],
        'login': ["laowang", "sstm"]
    }

    return {"status": "OK", "spiders": spdiers}

@app.post("/start/{spider_name}")
def start(spider_name: str, params: dict = None):
    global spider_manager
    # print(f'api 接收到的 spider ： {spider_name}')
    params = params or {}
    try:
        spider_manager.run_spider(spider_name, **params)
        return {"message": f"Started {spider_name}"}
    except Exception as e:
        return {"message": f"Failed to start {spider_name}: {str(e)}"}


def run_api():
    global spider_manager
    spider_manager.register("danbooru", DanbooruScraper)
    spider_manager.register("laowang", Laowang)
    spider_manager.register("hanime", HAnimeScraper)
    spider_manager.register("sstm", SSTM)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_api()