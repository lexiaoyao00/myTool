# from .page import BasePage
from .home import HomePage
from .page import BasePage
from .naviator import Navigator
from .router import register_route,RouteManager

from .danbooru import DanbooruPage,DanbooruDetailPage
from .hanime import HanimePage


__all__ = [
    "BasePage",
    "register_route",
    "RouteManager",
    "Navigator",
    "HomePage",
    "DanbooruPage",
    "DanbooruDetailPage",
    "HanimePage",
]