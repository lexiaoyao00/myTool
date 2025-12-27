import sys
import os

# 把 src 目录加到搜索路径的最前面
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))




from core.config import ConfigManager

if __name__ == "__main__":
    # 首次初始化必须传文件路径
    config_file = 'config/spider.toml'
    config = ConfigManager(config_file)

    # 像字典一样访问
    # print(config["database"]["server"])

    # 用点号路径访问嵌套值
    print(config.get("database.server","127.0.0.1"))

    # 修改配置
    config["title"] = "New Title"
    config.set("database.server", "127.0.0.1")

    # 保存到文件
    config.save()

    # 再次获取实例（不会重新加载）
    config2 = ConfigManager()
    print(config2["title"])  # 'New Title'