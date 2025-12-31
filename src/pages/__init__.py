# from .page import BasePage
from .home import HomePage
from .page import BasePage
from .danbooru import DanbooruPage
from .naviator import Navigator
from .router import register_route,RouteManager


__all__ = [
    "BasePage",
    "register_route",
    "RouteManager",
    "Navigator",
    "HomePage",
    "DanbooruPage",
]