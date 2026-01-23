from typing import List,Optional,overload,override,Callable
import curl_cffi
from curl_cffi import Response,AsyncSession,HeaderTypes,CookieTypes,Session
import asyncio
from loguru import logger
from pathlib import Path
import aiofiles
import time

class Spider:
    def __init__(self,headers:HeaderTypes=None, cookies:CookieTypes=None, chunk_size:int = 1024*1024*10, max_concurrent:int = 5):
        """
        :param headers: 请求头字典
        :param chunk_size: 每次写入的分块大小（字节），默认 1MB
        """
        self.headers = headers
        self.cookies = cookies
        self.chunk_size = chunk_size
        self.impersonate='chrome'
        self.max_concurrent = max_concurrent
        # self.semaphore = asyncio.Semaphore(max_concurrent)

    def syncGet(self, url:str, session:Session = None):
        if session is None:
            response:Response = curl_cffi.get(url=url, headers=self.headers,cookies=self.cookies, impersonate=self.impersonate)
        else:
            response:Response = session.get(url=url, headers=self.headers,cookies=self.cookies, impersonate=self.impersonate)

        if response is None:
            return None

        if response.status_code != 200:
            logger.warning(f"Failed to scrape, status code: {response.status_code}")
            return None

        logger.debug(f"Scraped {url} successfully")
        return response


    async def asyncGet(self, url:str):
        async with AsyncSession() as s:
            task = s.get(url=url, headers=self.headers, cookies=self.cookies, impersonate=self.impersonate,allow_redirects=True)
            try:
                result:Response = await task
                return result
            except Exception as e:
                logger.error(f"Failed to scrape, error: {e}")
                return None

    async def asyncGetMulties(self, urls:List[str]):
        async with AsyncSession() as s:
            tasks = []
            for url in urls:
                task = s.get(url=url, headers=self.headers, cookies=self.cookies, impersonate=self.impersonate)
                tasks.append(task)

            try:
                results:List[Response] = await asyncio.gather(*tasks)
                return results
            except Exception as e:
                logger.error(f"Failed to scrape, error: {e}")
                return None


    def download_sync(self, url: str, save_path: Path, on_progress = None) -> str:
        """同步下载（流式分块写入）"""
        save_path.parent.mkdir(parents=True, exist_ok=True)

        resp = curl_cffi.get(url, headers=self.headers, stream=True)
        if resp.status_code != 200:
            # raise Exception(f"下载失败: HTTP {resp.status_code}")
            logger.error(f"下载 {save_path} 失败: HTTP {resp.status_code}")
            return None

        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)

        logger.info(f"同步下载完成: {url} -> {save_path}")
        return str(save_path)

    async def download_async(self, url: str, save_path: Path, on_progress : Callable[[str, int, int], None] = None, name:str = None) -> str:
        """异步下载（流式分块写入）"""
        async with asyncio.Semaphore(self.max_concurrent):
            save_path.parent.mkdir(parents=True, exist_ok=True)

            async with AsyncSession(max_clients=5) as session:
                async with session.stream("GET", url, headers=self.headers) as resp:
                    if resp.status_code != 200:
                        # raise Exception(f"下载失败: HTTP {resp.status_code}")
                        logger.info(f"下载 {save_path} 失败: HTTP {resp.status_code}")
                        return None

                    total = int(resp.headers.get("Content-Length", 0))
                    downloaded = 0
                    last_report_time = time.time()

                    async with aiofiles.open(save_path, "wb") as f:
                        async for chunk in resp.aiter_content(chunk_size=self.chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)

                            now = time.time()
                            if on_progress and (now - last_report_time >= 1 or downloaded >= total):
                                task_name = name or url
                                on_progress(task_name, downloaded, total)
                                last_report_time = now

            logger.info(f"异步下载完成: {url} -> {save_path}")
            return str(save_path)


    def download(self, url: str, save_path: str|Path, async_mode: bool | None = None):
        """
        同步/异步下载统一接口
        :param url: 下载链接
        :param save_path: 保存路径
        :param async_mode: True=异步, False=同步, None=自动检测
        """
        path = Path(save_path).resolve()

        # 自动检测是否在事件循环中
        if async_mode is None:
            try:
                asyncio.get_running_loop()
                async_mode = True
            except RuntimeError:
                async_mode = False

        if async_mode:
            # 异步模式
            return self.download_async(url, path)
        else:
            # 同步模式
            return self.download_sync(url, path)


if __name__ == '__main__':
    headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://danbooru.donmai.us/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        }
    spider = Spider(headers=headers)
    dest_path = spider.download(url='https://cdn.donmai.us/original/39/0b/__ellen_joe_zenless_zone_zero_drawn_by_aznyan07_dab_neko_hentaudio_and_hiduki_voice_actor__390ba69860bc2cb20897aa0219aacb4f.mp4?download=1',
                    save_path='download/test.mp4')

    print(dest_path)
