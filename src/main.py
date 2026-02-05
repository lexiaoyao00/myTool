# from pages import Router
import time
import flet as ft
from loguru import logger
import asyncio
from db import init_db,close_db

from pages import Navigator, RouteManager
from multiprocessing import Process
from core.config import PRO_DIR


log_dir = PRO_DIR / 'storage/logs'
# logger.remove()
logger.add(f"{str(log_dir)}/debug.log", enqueue=True, rotation="10 MB",level="DEBUG")
logger.add(f"{str(log_dir)}/info.log", enqueue=True, rotation="10 MB",level="INFO")
logger.add(f"{str(log_dir)}/warning.log", enqueue=True,rotation="10 MB", level="WARNING")
logger.add(f"{str(log_dir)}/error.log", enqueue=True,rotation="10 MB", level="ERROR")

# 应用
class MyApp:
    def main(self, page: ft.Page):
        page.title = "my app"
        page.scroll = ft.ScrollMode.AUTO

        nav = Navigator(page)

        self.rm = RouteManager(page, nav)
        page.on_route_change = self.rm.route_change
        page.go("/")   # 进入首页
        nav.current = "/"  # 初始化当前路由

    def run(self):
        ft.app(target=self.main)


def main():

    from api.app import run_api

    p = Process(target=run_api)
    p.start()

    time.sleep(1)
    MyApp().run()

    p.terminate()
    p.join()



async def test():

    await init_db()

    from db.models.missav import Missav,Actress,Actor,Genre,Series,Maker,Director,Tag
    from tortoise.expressions import Q
    from tortoise.functions import Count
    # av = await Missav.create(releasedate='2017-02-19',
    #                    title='銀粉奴●演奏家 二宮和香',
    #                    num_code='ABG-004-UNCENSORED-LEAK')

    # ma = await Actor.create(name='堀尾')
    # fa = await Actress.create(name='二宫和香')

    # g1 = await Genre.create(name='无码流出')
    # g2 = await Genre.create(name='巨乳')
    # g3 = await Genre.create(name='恋物癖')

    # s = await Series.create(name='○粉奴●')

    # m = await Maker.create(name='ゴールドバグ/妄想族')

    # d = await Director.create(name='あばしり一家')

    # t = await Tag.create(name='ゴールドバグ')

    # await av.actors.add(ma)
    # await av.actresses.add(fa)
    # await av.genres.add(g1,g2,g3)
    # await av.series.add(s)
    # await av.makers.add(m)
    # await av.directors.add(d)
    # await av.tags.add(t)

    # posts = await Missav.all().prefetch_related("tags", "genres")
    # for post in posts:
    #     print(f"Post: {post.title}")
    #     print(f"Tags: {[tag.name for tag in await post.tags.all()]}")
    #     print(f"Genres: {[genre.name for genre in await post.genres.all()]}")
    #     print('=' * 20)

    # print(len(posts))

    # posts = await Missav.filter(tags__name='巨乳').filter(tags__name='美丽的胸部')
    # for post in posts:
    #     print(f"Post: {post.title}")
    #     print(f"Tags: {[tag.name for tag in await post.tags.all()]}")
    #     print(f"Genres: {[genre.name for genre in await post.genres.all()]}")
    #     print('=' * 20)

    # print(len(posts))

    # filter_tag_conditions = ['户外曝晒']
    # posts = await Missav.filter(
    #     tags__name__in=filter_tag_conditions
    #     ).annotate(
    #         tag__count = Count('tags')
    #     ).filter(
    #         tag__count=len(filter_tag_conditions)
    #     )

    # for post in posts:
    #     print(f"Post: {post.title}")
    #     print(f"url: {post.url}")
    #     print(f"Tags: {[tag.name for tag in await post.tags.all()]}")
    #     print(f"Genres: {[genre.name for genre in await post.genres.all()]}")
    #     print('=' * 20)

    # print(len(posts))

    # tags = await Tag.all()
    # for tag in tags:
    #     print(tag.name , tag.href)

    # print(len(tags))

    posts_count = await Missav.all().count()
    print(posts_count)



    await close_db()



if __name__ == '__main__':
    # asyncio.run(test())
    main()
    # ft.app(target=main)