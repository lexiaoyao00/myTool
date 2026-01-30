from .config import Config, ConfigManager,PRO_DIR
from typing import Dict

class Setting:
    _instance = None

    def __new__(cls):
        # 单例模式
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path_config: str = 'config/path.toml'):
        self.config_manager = ConfigManager()
        self._settings : Dict[str, Config] = {}     # 别称 -> 配置

        self._settings['path'] = self.config_manager.getConfig(path_config)


    def get_config(self, alias: str) -> Config:
        return self._settings.get(alias)

    def save_settings(self):
        for config in self._settings.values():
            config.save()
