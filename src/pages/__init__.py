# from .page import BasePage
from .home import HomePage
from .setting import SettingPage
from .base_page import BasePage
from .naviator import Navigator
from .router import register_route,RouteManager

from .danbooru import DanbooruPage,DanbooruDetailPage
from .hanime import HanimePage
from .exhentai import ExhentaiPage
from .missav import MissavPage


__all__ = [
    "BasePage",
    "register_route",
    "RouteManager",
    "Navigator",
    "HomePage",
    "SettingPage",
    "DanbooruPage",
    "DanbooruDetailPage",
    "HanimePage",
    "ExhentaiPage",
    "MissavPage",
]