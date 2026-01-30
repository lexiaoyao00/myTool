import asyncio
from tortoise import Tortoise
from models import Author, Post, Tag


async def run():
    TORTOISE_ORM = {
        "connections": {
            "default": "sqlite://db.sqlite3",
        },
        "apps": {
            "models": {
                "models": ["models"],  # 模型模块
                "default_connection": "default",
            },
        },
    }

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # === 一对多 ===
    author = await Author.create(name="Alice")
    post1 = await Post.create(title="First Post", content="Hello ORM!", author=author)
    post2 = await Post.create(title="Second Post", content="Another content", author=author)

    # === 多对多 ===
    tag_python = await Tag.create(name="Python")
    tag_orm = await Tag.create(name="ORM")

    # 给 post1 添加两个标签
    await post1.tags.add(tag_python, tag_orm)

    # 给 post2 添加一个标签
    await post2.tags.add(tag_orm)

    # 查询：每个 Post 的所有标签
    posts = await Post.all().prefetch_related("tags", "author")
    for p in posts:
        print(f"\nPost: {p.title}")
        print(f"Author: {p.author.name}")
        print("Tags:", [t.name for t in await p.tags.all()])

    # 查询反向关系：哪些 Post 拥有某个 Tag
    tag = await Tag.get(name="ORM").prefetch_related("posts")
    print(f"\nTag '{tag.name}' is used in posts:",
          [p.title for p in await tag.posts.all()])

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run())
