

from core.config import ConfigManager
from pathlib import Path

config_manaer = ConfigManager()

download_path = config_manaer.getConfig('config/path.toml').get('download_path')
data_path = config_manaer.getConfig('config/path.toml').get('data_path')





from .page import DanbooruPage
from .detaile import DanbooruDetailPage
__all__ = [
    "DanbooruPage",
    "DanbooruDetailPage"
]