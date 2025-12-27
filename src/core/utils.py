import enum
from typing import Dict, List, Optional


class FileType(enum.Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    OTHER = 'other'

def judge_file_type(file_path:str) -> str:
    file_suffix = file_path.split('.')[-1].lower()
    if file_suffix in ['jpg','jpeg','png','gif']:
        return FileType.IMAGE
    elif file_suffix in ['mp4','webm','mkv']:
        return FileType.VIDEO
    else:
        return file_suffix

class CommandType(enum.Enum):
    START = 'start'
    STOP = 'stop'

class TopicName(enum.Enum):
    SPIDER = 'spider'
    LOGIN = 'login'


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