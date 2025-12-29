# from .page import BasePage
from .home import HomePage
# from .page import Router
from .danbooru import DanbooruPage
from .router import register_route,RouteManager,Navigator


__all__ = [
    # "BasePage",
    "register_route",
    "RouteManager",
    "Navigator",
    # "Router",
    "HomePage",
    "DanbooruPage",
]