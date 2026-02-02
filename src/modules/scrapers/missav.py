from ..crawler import Crawler
from typing import List,Optional
from curl_cffi import Session,Response
from core.spider import Spider
from parsel import Selector
from yarl import URL
from loguru import logger
from pydantic import BaseModel
from datetime import date
import re
import asyncio
from db.models.missav import (
    Missav,
    Actress,
    Actor,
    Genre,
    Series,
    Maker,
    Director,
    Tag
    )


missav_cookies = {
    # '_ga': 'GA1.1.1662984184.1757159641',
    # 'user_uuid': '31739f6d-7176-4128-b902-ddc265a04d55',
    # 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6Ik1sUlNqZ05wUlRpTHFyQzFhZG5VR2c9PSIsInZhbHVlIjoiNUpkZU1neXcydnpxYTBWT0lWUWR6aUJpckdlYU9qaU1pYU9JNVhXUWRnampMYnBZTUU2T3ZvbE1tSCtHbzFDMThpdUcxVVVHb0dEaDVrVTBKVTFMT3RwanJQQ3B5Y1l5cEtUT0RmMmdwNXhvVkVTSk9ZNDQyTWt0VnJyUUFPNnVOcWhoVWJGbTNXTTV1NEEra2Ftc0s0OSsrbm8xZ2JTWlRxcDdWa3VEUnNJR1RiMW12ajdkdGNLaVliOFVsMUlaQzR1azdFaW05ZUpRVmZwT2orbmNOR0hKWS9PekxYOW5GL2xDZEZyVnNzOD0iLCJtYWMiOiI4YTRkNWVkMDMzM2VhZGE0MTRjM2JlMmJiNmVhMDk3MGQ0NDlhNWQ2OWYyMjdiZGE2YWJkMDFmZmNmNzZmM2NlIiwidGFnIjoiIn0%3D',
    # '_ga_9FFNX13PHD': 'deleted',
    # 'search_history': '[%22MIDE-565%22%2C%22n1335%22%2C%22012419-846%22%2C%22pdd-004%22%2C%22NHDT-354%22%2C%22rctd-339%22]',
    # 'cf_clearance': 'C3xf33B5AJA1y9VgeLnmopO.bBk2.FzNExkJSTMLIak-1768556342-1.2.1.1-gkWNIV48XFBWaXUt_H8g4Ltq7EjQDEaN_ZAqkKfJ3ZcJJeRERxzFngfh4_RXo4z9qruUaAFWhUc3uXFNgVR22IzN_lmivy.1vkLBfjM_3ihZQi4Ct_tuATOtJbLsOvwnO_qoKSk9oPEC3DtqwlwLbkmp37DU9ENoxUo9LHycPb628bQAgYThzQwjULKm3ND.B2I5fzB3ArT8nJrY_y2k6._DcgMwNo6oq9xc_G9EktE',
    # 'XSRF-TOKEN': 'eyJpdiI6ImtHenRucjVrNVBTMlNUV2s2VjREekE9PSIsInZhbHVlIjoiMW1iMDhJM1ZKNmlDUnJIUFczUDlhbzVveFk4UGNqNmRXYlhkS014TnRhNzhpVy9SQmQ4SUZjN255TEdmTTZzdlMwQ2cyQkxMRjlvbTdsMnE1Q29xeGx4TjVGQU1qNVhRV1JVbUdlaTMvemNLQUhIaE5lOE1ja0tnTXNOZ1U3VE8iLCJtYWMiOiJkMTM3Mzg0ODRjYWQ4MjAyYjEwMjI0OGRjNjcyMTZlNGMwN2Q4YmViY2U4NjczM2FjZGI1M2Y4OTMxNTg0ZTdiIiwidGFnIjoiIn0%3D',
    # 'missav_session': 'eyJpdiI6Ik9TMThrVnRoWE9SZjVZLy8vWFV6L0E9PSIsInZhbHVlIjoiZjhxb2tqcU00N051T0IzNC9nTTJMVjNtdk94cnZTYzdFNEVQME5DN1pHVFdhbEJkV1FnZTFUNmd1allENU1PN3hVNTBzc0tBVDVqV2ZON3lXNUtqK21qZGFjLzBOQy9JZSt2Nno2Ynd4dytZYkk0R1JKV3h0cDZrMDhyT3VSVkwiLCJtYWMiOiJmZmEzYTYyNTA5MTBhNTA2MDQ1NWU4YjI4MTNkMzYyYWE0NTVmYjc1ZWYzYTdlYjJiZjU2Mjc0YmM4MTIzMTY4IiwidGFnIjoiIn0%3D',
    # 'LOWktJd4g3hAiYlDrtiysQX07e82Rt02VEaredL5': 'eyJpdiI6Im1QbHFRVW5SYS9EN1EyMGZWMktrS1E9PSIsInZhbHVlIjoiZktuYVBqVkRXUjZ0eTR6M2tlV0Jmb2kzSzlvdXpEcUFUZGV3SUtxR09xN3NqSFlVemhLQUlzYkxzQm5teVljTjZmVnRRdFNjS0F6blFoQXRQNWNVTUR2L01rTTRsU0IzVDYwd2dROUZHM3Zma3dxL0xvTVpjWmx1TzIxeStybTgySDh1TWI2VlpGMlZtVEh4bUdtSElpMW5uaEIydGJGWEZKSjZSUkFsREMyc0RtRUd2ZVBrcUdHRWlWOCtBRW9FMkJ5QjgzWnpEQ2ZjcW13Vzdjd0U0aUQrQkhCaFdNT2huUEhZeEVsOUFOTFhPOG5SZ1pPOUU4RVpjZEtlbHV5K2NJbEpZeU1lMi9CKzFUbCs2OFRJckdTZGxVVVNqTXhwaW5YZy9PdGVPWHZJTC9GS1JwUGR4TDZGNHJDbHlrZm4yRlNZRkszck5QMElGaVphVTVoRGZXS2w3RGlmNDNZNlpicklrcjFzNlpWVXdHNFB3dW9HTC9kMzliV25PaXEwMmN2eXJZQ3p1a0NNV2ZZR3FJNnROSEdtUExaNExSazVDNHFGNUZtU3dTdisxNjNvY1V0K2F4dWRrbEc4WDVsY0Jsbk9JQU9PUG9BNWZkVmxwdVVWaUU4ZWJkdi9GM2NHcTlpeG1ZQXpKZFg4ZXgza1cwK0tLTnd6dmNYQXRHN1I1QWxjWUN1enZuL2tRcUJybGVZeWU3MjRFUlV3c09BMC8vRVNKUDJCSmE3YTZrdEE3bzhMSGRjZFdNN0g1RTZKY1BvZmgzT3JyNDZkT20rL1NZUWhVSThGNDJCZDVHdG9Jc0NjMm02a21Ccz0iLCJtYWMiOiJhNmE0NWY0MGFiOWNjYjQ5OTMzMzQ5NzYxODFhM2RkNmMwMmRiMDg5Y2RhMDVlZWIyMTYxZDZmZTIxNTQxMTE5IiwidGFnIjoiIn0%3D',
    # '_ga_WVQPWV98M1': 'GS2.1.s1768554667$o13$g1$t1768556359$j19$l0$h0',
}

missav_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    # 'if-modified-since': 'Fri, 16 Jan 2026 05:26:38 GMT',
    'priority': 'u=0, i',
    'referer': 'https://missav.ws',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.193"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.193", "Chromium";v="143.0.7499.193", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

class ItemSearchResult(BaseModel):
    title: str
    post_url: str
    pre_img: str


class EasyMode(BaseModel):
    name : str
    href : str = None

class ItemWatchInfo(BaseModel):
    title : str = None
    num_code : str = None
    releasedate : date = None
    plot : str = ''
    actresses : List[EasyMode] = []
    actors : List[EasyMode] = []
    genres : List[EasyMode] = []
    series : List[EasyMode] = []
    makers : List[EasyMode] = []
    directors : List[EasyMode] = []
    tags : List[EasyMode] = []


class MissavWatch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session

        self._label_func_map = {
            '发行日期': self._parseWatchInfo_date,
            '番号': self._parseWatchInfo_num_code,
            '标题': self._parseWatchInfo_title,
            '女优': self._parseWatchInfo_actresses,
            '男优': self._parseWatchInfo_actors,
            '类型': self._parseWatchInfo_genres,
            '系列': self._parseWatchInfo_series,
            '发行商': self._parseWatchInfo_makers,
            '导演': self._parseWatchInfo_directors,
            '标籤': self._parseWatchInfo_tags,
        }


    def _parseWatchInfo_date(self,sel:Selector,item:ItemWatchInfo):
        date_time = sel.css('time.font-medium::text').get()
        if date_time:
            item.releasedate = date_time
            return True
        else:
            logger.warning('date_time is None')
            return False

    def _parseWatchInfo_title(self,sel:Selector,item:ItemWatchInfo):
        title = sel.css('span.font-medium::text').get()
        if title:
            item.title = title
            return True
        else:
            logger.warning('title is None')
            return False

    def _parseWatchInfo_num_code(self,sel:Selector,item:ItemWatchInfo):
        num_code = sel.css('span.font-medium::text').get()
        if num_code:
            item.num_code = num_code
            return True
        else:
            logger.warning('num_code is None')
            return False

    def _parseWatchInfo_actresses(self,sel:Selector,item:ItemWatchInfo):
        actresses_sel = sel.css('a.font-medium')
        if not actresses_sel.get():
            logger.warning('actresses is None')
            return False

        for actress in actresses_sel:
            name = actress.css('::text').get()
            href = actress.css('::attr(href)').get()
            item.actresses.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_actors(self,sel:Selector,item:ItemWatchInfo):
        actors_sel = sel.css('a.font-medium')
        if not actors_sel.get():
            logger.warning('actors is None')
            return False

        for actor in actors_sel:
            name = actor.css('::text').get()
            href = actor.css('::attr(href)').get()
            item.actors.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_genres(self,sel:Selector,item:ItemWatchInfo):
        genres_sel = sel.css('a.font-medium')
        if not genres_sel.get():
            logger.warning('genres is None')
            return False

        for genre in genres_sel:
            name = genre.css('::text').get()
            href = genre.css('::attr(href)').get()
            item.genres.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_series(self,sel:Selector,item:ItemWatchInfo):
        series_sel = sel.css('a.font-medium')
        if not series_sel.get():
            logger.warning('series is None')
            return False

        for series in series_sel:
            name = series.css('::text').get()
            href = series.css('::attr(href)').get()

            item.series.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_makers(self,sel:Selector,item:ItemWatchInfo):
        makers_sel = sel.css('a.font-medium')
        if not makers_sel.get():
            logger.warning('makers is None')
            return False

        for maker in makers_sel:
            name = maker.css('::text').get()
            href = maker.css('::attr(href)').get()
            item.makers.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_directors(self,sel:Selector,item:ItemWatchInfo):
        directors_sel = sel.css('a.font-medium')
        if not directors_sel.get():
            logger.warning('directors is None')
            return False

        for director in directors_sel:
            name = director.css('::text').get()
            href = director.css('::attr(href)').get()
            item.directors.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo_tags(self,sel:Selector,item:ItemWatchInfo):
        tags_sel = sel.css('a.font-medium')
        if not tags_sel.get():
            logger.warning('tags is None')
            return False

        for tag in tags_sel:
            name = tag.css('::text').get()
            href = tag.css('::attr(href)').get()
            item.tags.append(EasyMode(name=name,href=href))

        return True

    def _parseWatchInfo(self,html:str):
        sel = Selector(text=html)

        item = ItemWatchInfo()

        plot = sel.css('div.mb-1.text-secondary.break-all.line-clamp-2::text').get()
        if plot:
            item.plot = plot.strip()

        space_info_sel = sel.css('div.space-y-2 div.text-secondary')

        for space_info in space_info_sel:
            key = space_info.css('span:first-child::text').get().strip(':').strip()
            if key not in self._label_func_map:
                logger.warning(f'key {key} 是预料之外的分类键值')
                continue

            func = self._label_func_map[key]
            if not func(space_info,item):
                logger.warning(f'key {key} 的值解析失败')
                return None

        return item



    async def getWatchInfo(self, url:str|URL):
        res : Response = await self.spider.asyncGet(str(url))
        if res is None:
            logger.error(f"[MissavWatchInfo getWatchInfo] {str(url)} failed to get response")
            return None

        if res.status_code not in [200, 302]:
            logger.error(f"[MissavWatchInfo getWatchInfo] {str(url)} status code {res.status_code}")
            return None

        return self._parseWatchInfo(res.text)


class MissavSearch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session
        self.base_url = 'https://missav.ws/cn/search'


    def _parseSearchMaxPage(self,html:str) -> int:
        sel = Selector(text=html)
        max_page_sel = sel.css('span#price-currency::text').get()
        if not max_page_sel:
            return 1

        max_page_match = re.search(r'\d+', max_page_sel)
        if not max_page_match:
            return 1

        max_page = int(max_page_match.group())
        return max_page

    def _parseSearchResults(self,html:str):
        sel = Selector(text=html)
        posts_sel = sel.css('div.relative.rounded.overflow-hidden.shadow-lg a:first-child')
        if not posts_sel:
            return None


        items : List[ItemSearchResult] = []
        for post_sel in posts_sel:
            url = post_sel.css('::attr(href)').get()
            title = post_sel.css('img::attr(alt)').get()
            pre_img = post_sel.css('img::attr(data-src)').get()
            item = ItemSearchResult(
                title = title,
                post_url = url,
                pre_img = pre_img
            )
            items.append(item)

        return items

    async def getPostPreviews(self,query:str):
        search_url = URL(self.base_url) / query
        return await self.getSearchResults(search_url)

    async def getSearchResults(self, url:str|URL, sem: Optional[asyncio.Semaphore] = None):
        if sem:
            async with sem:
                res:Response = await self.spider.asyncGet(str(url))
        else:
            res:Response = await self.spider.asyncGet(str(url))

        if res is None:
            logger.error(f"[MissavSearch getSearchResults] {str(url)} failed to get response")
            return None

        if res.status_code == 404:
            logger.error(f"[MissavSearch getSearchResults] {str(url)} not found")
            return None

        return self._parseSearchResults(res.text)

    async def getSearchResultsAllPages(self, search_url:str|URL):
        res:Response = await self.spider.asyncGet(str(search_url))
        if res is None:
            logger.error(f"[MissavSearch getSearchResultsAllPages] {str(search_url)} failed to get response")
            return None

        if res.status_code == 404:
            logger.error(f"[MissavSearch getSearchResultsAllPages] {str(search_url)} not found")
            return None

        max_page = self._parseSearchMaxPage(res.text)
        # print(max_page)
        if max_page == 1:
            return await self.getSearchResults(search_url)

        base_url = URL(search_url)
        urls = [ base_url.update_query(page=i) for i in range(1,max_page+1) ]
        tasks = [ asyncio.create_task(self.getSearchResults(url)) for url in urls ]

        total = len(tasks)
        completed = 0
        items : List[ItemSearchResult] = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                items.extend(result)
            completed += 1
            logger.info(f"[MissavSearch getSearchResultsAllPages] {completed}/{total} completed")

        return items


class MissavScraper(Crawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = Session()
        self.spider = Spider(
            headers = missav_headers,
            cookies = missav_cookies
        )

        self._searcher = MissavSearch(self.spider,self.session)
        self._watcher = MissavWatch(self.spider,self.session)

    async def run(self, **kwargs):

        scrape_type = kwargs.get('scrape_type')

        if scrape_type == 'search':
            url = kwargs.get('url')
            if url:
                # items = await self._searcher.getSearchResults(url)
                items = await self._searcher.getSearchResultsAllPages(url)
            else:
                query = kwargs.get('query','露出')
                items = await self._searcher.getPostPreviews(query)

            if not items:
                logger.error(f"[MissavScraper] 搜索失败")
                self.queue.put({
                    "status": "failed",
                    "type" : "search",
                    "message": f"搜索 {url or query} 未爬取到信息"
                })
                return

            res_list = [item.model_dump() for item in items]
            self.queue.put({
                "status": "success",
                "type" : "search",
                "data":res_list,
            })
            logger.info(f"[MissavScraper] 搜索成功, 共 {len(items)} 条数据")
        elif scrape_type == 'watch':
            url = kwargs.get('url')

            if not url:
                logger.error(f"[MissavScraper] watch url 为空")
                self.queue.put({
                    "status": "failed",
                    "type" : "watch",
                    "message": f"URL 为空，无法爬取"
                })

            item = await self._watcher.getWatchInfo(url)
            if not item:
                logger.error(f"[MissavScraper] watch 爬取失败")
                self.queue.put({
                    "status": "failed",
                    "type" : "watch",
                    "message": f"爬取 {url} 失败"
                })
                return

            await self.uploadWatchInfo(item)
            self.queue.put({
                "status": "success",
                "type" : "watch",
                "data":item.model_dump(exclude_none=True),
            })

        else:
            await self.test()

    async def uploadWatchInfo(self, item:ItemWatchInfo):

        av = await Missav.get_or_none(num_code=item.num_code)
        if av:
            logger.info(f"[MissavScraper] {item.num_code} 已存在")
            return

        av = await Missav.create(releasedate = item.releasedate,
            num_code = item.num_code,
            title = item.title,
            plot = item.plot)

        pending_actresses = []
        for actress in item.actresses:
            fa = await Actress.get_or_none(name=actress.name)
            if fa:
                pending_actresses.append(fa)
            else:
                fa = await Actress.create(name=actress.name,href=actress.href)
                pending_actresses.append(fa)
        if pending_actresses:
            await av.actresses.add(*pending_actresses)

        pending_actors = []
        for actor in item.actors:
            ma = await Actor.get_or_none(name=actor.name)
            if ma:
                pending_actors.append(ma)
            else:
                ma = await Actor.create(name=actor.name,href=actor.href)
                pending_actors.append(ma)
        if pending_actors:
            await av.actors.add(*pending_actors)

        pending_genres = []
        for genre in item.genres:
            ga = await Genre.get_or_none(name=genre.name)
            if ga:
                pending_genres.append(ga)
            else:
                ga = await Genre.create(name=genre.name)
                pending_genres.append(ga)
        if pending_genres:
            await av.genres.add(*pending_genres)

        pending_series = []
        for series in item.series:
            sa = await Series.get_or_none(name=series.name)
            if sa:
                pending_series.append(sa)
            else:
                sa = await Series.create(name=series.name,href=series.href)
                pending_series.append(sa)
        if pending_series:
            await av.series.add(*pending_series)

        pending_makers = []
        for maker in item.makers:
            ma = await Maker.get_or_none(name=maker.name)
            if ma:
                pending_makers.append(ma)
            else:
                ma = await Maker.create(name=maker.name,href=maker.href)
                pending_makers.append(ma)
        if pending_makers:
            await av.makers.add(*pending_makers)

        pending_directors = []
        for director in item.directors:
            da = await Director.get_or_none(name=director.name)
            if da:
                pending_directors.append(da)
            else:
                da = await Director.create(name=director.name,href=director.href)
                pending_directors.append(da)
        if pending_directors:
            await av.directors.add(*pending_directors)

        pending_tags = []
        for tag in item.tags:
            ta = await Tag.get_or_none(name=tag.name)
            if ta:
                pending_tags.append(ta)
            else:
                ta = await Tag.create(name=tag.name)
                pending_tags.append(ta)
        if pending_tags:
            await av.tags.add(*pending_tags)

        await av.save()

    async def test(self):
        items = await self._searcher.getPostPreviews('mide-565')
        if not items:
            print('no items')

        for item in items:
            print(item.title)
            print(item.post_url)
            print(item.pre_img)
            print('---')