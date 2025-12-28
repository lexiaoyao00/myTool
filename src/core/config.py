import toml
from pathlib import Path
from typing import Any,Dict


class Config:
    _instance = None
    _data: dict = {}
    _file_path: Path = None

    def __new__(cls, file_path: str | Path = None):
        # 单例模式
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if file_path is None:
                raise ValueError("首次初始化必须提供配置文件路径")
            cls._file_path = Path(file_path)
            cls._load()
        return cls._instance

    @classmethod
    def _load(cls):
        """加载 TOML 文件到内存"""
        cls._data = toml.load(cls._file_path)

    def save(self):
        """保存当前配置到文件"""
        with open(self._file_path, "w", encoding="utf-8") as f:
            toml.dump(self._data, f)

    def reload(self):
        """重新加载配置文件"""
        self._load()

    def keys(self):
        return self._data.keys()

    # ---- 字典访问支持 ----
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    # ---- 额外的 get/set 方法支持点号路径 ----
    def get(self, path: str, default=None) -> Any:
        parts = path.split(".")
        current = self._data
        for p in parts:
            if isinstance(current, dict) and p in current:
                current = current[p]
            else:
                return default
        return current

    def set(self, path: str, value: Any):
        parts = path.split(".")
        current = self._data
        for p in parts[:-1]:
            if p not in current or not isinstance(current[p], dict):
                current[p] = {}
            current = current[p]
        current[parts[-1]] = value



class ConfigManager:
    _instance = None
    def __new__(cls):
        # 单例模式
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.config_map : Dict[str, Config] = {}

    def getConfig(self,file_path: str | Path) -> Config:
        if file_path not in self.config_map:
            self.config_map[file_path] = Config(file_path)
        return self.config_map[file_path]

    def reload(self,file_path: str | Path):
        if file_path not in self.config_map:
            self.config_map[file_path] = Config(file_path)
        else:
            self.config_map[file_path].reload()

    def save(self,file_path: str | Path):
        if file_path in self.config_map:
            self.config_map[file_path].save()

    def save_all(self):
        for config in self.config_map.values():
            config.save()