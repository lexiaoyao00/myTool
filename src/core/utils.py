import enum
from typing import Dict, List, Iterable, Awaitable, Any, List
import zipfile
from pathlib import Path
import asyncio

async def limit_gather(coros: Iterable[Awaitable[Any]], limit: int) -> List[Any]:
    """
    对一组协程任务执行 gather，但限制同时运行的最大数量。

    参数:
        coros: 一个可迭代对象，包含协程对象 (coroutine)。
               例如 [download_async(...), download_async(...), ...]
        limit: 同时并发执行的最大协程数。

    返回值:
        返回 gather 的结果列表，与 asyncio.gather 一致。
    """
    sem = asyncio.Semaphore(limit)

    async def run_with_sem(coro: Awaitable[Any]):
        async with sem:
            return await coro

    return await asyncio.gather(*(run_with_sem(c) for c in coros))


def zip_dir(folder_path, zip_path, include_dirs: bool = False):
    """
    使用 pathlib 遍历目录并压缩到 zip 文件
    :param folder_path: 要压缩的目录路径（str 或 Path）
    :param zip_path: 生成的 zip 文件路径（str 或 Path）
    :param include_dirs: 是否在压缩包中包含目录（即使目录为空）
    """
    folder_path = Path(folder_path)
    zip_path = Path(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in folder_path.rglob("*"):
            # 如果是文件就直接写
            if path.is_file():
                arcname = path.relative_to(folder_path)
                zipf.write(path, arcname)
            elif include_dirs and path.is_dir():
                # zip 文件中显式添加目录（保留空文件夹）
                arcname = path.relative_to(folder_path).as_posix() + '/'
                zinfo = zipfile.ZipInfo(arcname)
                zipf.writestr(zinfo, '')  # 目录内容为空

    # print(f"✅ 打包完成：{zip_path}")
    return zip_path

def add_file_to_zip(zip_path, file_path, arcname=None):
    zip_path = Path(zip_path)
    file_path = Path(file_path)

    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, arcname or file_path.name)
    # print(f"✅ 已添加 {file_path} 到 {zip_path}")


class FileType(enum.Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    OTHER = 'other'

def judge_file_type(file_path:str) -> FileType|str:
    file_suffix = file_path.split('.')[-1].lower()
    if file_suffix in ['jpg','jpeg','png','gif','webp']:
        return FileType.IMAGE
    elif file_suffix in ['mp4','webm','mkv']:
        return FileType.VIDEO
    else:
        return file_suffix

def curl_cffi_cookies_to_playwright(curl_cookies: Dict[str, str], domain: str) -> List[Dict]:
    """
    将 curl_cffi 的 cookies 转换为 Playwright 可用的 cookies 列表

    :param curl_cffi_cookies: curl_cffi 的 cookies (可以是 client.cookies 或简单字典)
    :param domain: 目标域名，比如 "example.com"
    :return: Playwright cookies 列表
    """
    result = []

    # 如果传的是 Cookies 对象 (类似 requests.cookies.RequestsCookieJar)
    # if hasattr(curl_cffi_cookies, "items"):
    #     iterable = curl_cffi_cookies.items()
    # elif isinstance(curl_cffi_cookies, dict):
    #     iterable = curl_cffi_cookies.items()
    # else:
    #     raise TypeError("Unsupported cookies type, must be dict or curl_cffi Cookies.")

    iterable = curl_cookies.items()

    for name, value in iterable:
        cookie_obj = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": "/",
            "httpOnly": False,
            "secure": False,
            "sameSite": "Lax",
        }
        result.append(cookie_obj)

    return result