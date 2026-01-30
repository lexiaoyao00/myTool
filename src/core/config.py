import toml
from pathlib import Path
from typing import Any,Dict


PRO_DIR = Path(__file__).parent.parent.parent

class Config:
    _data: dict = {}
    _file_path: Path = None

    def __init__(self, file_path: str | Path):
        self._file_path = Path(file_path).resolve()
        self._load()

    def _load(self):
        """加载 TOML 文件到内存"""
        self._data = toml.load(self._file_path)

    def save(self, file_path: str | Path = None):
        """保存当前配置到文件"""
        if file_path is None:
            file_path = self._file_path
        with open(file_path, "w", encoding="utf-8") as f:
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
    config_map : Dict[str, Config] = {}

    def __new__(cls):
        # 单例模式
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def __init__(self):
    #     self.config_map : Dict[str, Config] = {}

    def getConfig(self,file_path: str | Path) -> Config:
        path = Path(file_path)
        if path.is_absolute():
            resolve_path = str(path.resolve())
        else:
            resolve_path = PRO_DIR / path
        if resolve_path not in self.config_map:
            self.config_map[resolve_path] = Config(resolve_path)
        return self.config_map[resolve_path]

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

    def list_config(self):
        return self.config_map.keys()