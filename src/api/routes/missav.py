from fastapi import APIRouter
from schemas.missav import ItemWatchInfo
from db.models.missav import Missav,Actress,Actor,Genre,Series,Maker,Director,Tag
import asyncio


missav_router = APIRouter(prefix='/missav', tags=['missav'])
missav_queue = asyncio.Queue()
missav_stop_event = asyncio.Event()
missav_task = None

@missav_router.post('/upload')
async def save_item(item: ItemWatchInfo):
    """
    Save item to watch
    """
    await missav_queue.put(item)

    return {"status": "queued"}


async def worker():
    while not missav_stop_event.is_set():
        item : ItemWatchInfo = await missav_queue.get()
        await upload_to_db(item)
        missav_queue.task_done()

async def init_tasks():
    global missav_task
    print("init missav tasks")
    missav_stop_event.clear()
    missav_task = asyncio.create_task(worker())

async def shutdown_tasks():
    missav_stop_event.set()
    await missav_queue.join()
    if missav_task:
        await missav_task

    print("missav tasks shutdown")

async def upload_to_db(item: ItemWatchInfo):
    """上传到数据库"""
    av, created = await Missav.get_or_create(releasedate = item.releasedate,
            num_code = item.num_code,
            title = item.title,
            plot = item.plot,
            url= item.url)

    if not created:
        # logger.warning(f"Missav Item {item.title} 已经存在")
        print(f"Missav Item {item.title} 已经存在")
        return

    pending_actresses = []
    for actress in item.actresses:
        fa,_ = await Actress.get_or_create(name=actress.name,href=actress.href)
        pending_actresses.append(fa)
    if pending_actresses:
        await av.actresses.add(*pending_actresses)

    pending_actors = []
    for actor in item.actors:
        ma,_ = await Actor.get_or_create(name=actor.name,href=actor.href)
        pending_actors.append(ma)
    if pending_actors:
        await av.actors.add(*pending_actors)

    pending_genres = []
    for genre in item.genres:
        ga,_ = await Genre.get_or_create(name=genre.name,href=genre.href)
        pending_genres.append(ga)
    if pending_genres:
        await av.genres.add(*pending_genres)

    pending_series = []
    for series in item.series:
        sa,_ = await Series.get_or_create(name=series.name,href=series.href)
        pending_series.append(sa)
    if pending_series:
        await av.series.add(*pending_series)

    pending_makers = []
    for maker in item.makers:
        ma,_ = await Maker.get_or_create(name=maker.name,href=maker.href)
        pending_makers.append(ma)
    if pending_makers:
        await av.makers.add(*pending_makers)

    pending_directors = []
    for director in item.directors:
        da,_ = await Director.get_or_create(name=director.name,href=director.href)
        pending_directors.append(da)
    if pending_directors:
        await av.directors.add(*pending_directors)

    pending_tags = []
    for tag in item.tags:
        ta, _ = await Tag.get_or_create(name=tag.name, href=tag.href)
        pending_tags.append(ta)
    await av.tags.add(*pending_tags)


    await av.save()
    # logger.info(f"Missav Item {item.title} 上传完成")
    print(f"Missav Item {item.title} 上传完成")

