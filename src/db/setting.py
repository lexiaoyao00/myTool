import asyncio
from tortoise import Tortoise,connections

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db.sqlite3",
    },
    "apps": {
        "missav": {
            "models": ["db.models.missav"],  # 模型模块
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await connections.close_all()