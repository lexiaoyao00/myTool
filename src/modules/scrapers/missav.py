from ..crawler import Crawler
from typing import List,Optional
import curl_cffi
from curl_cffi import Session,Response
from parsel import Selector
from yarl import URL
from loguru import logger
import re
import asyncio
from core.spider import Spider
from core.utils import limit_gather
from schemas.missav import ItemSearchResult, EasyMode, ItemWatchInfo
from tortoise.functions import Count
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

    def _parseWatchInfo(self,html:str, url:str):
        sel = Selector(text=html)

        item = ItemWatchInfo()
        item.url = url

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
        url_str = str(url)
        res : Response = await self.spider.asyncGet(url_str)
        if res is None:
            logger.error(f"[MissavWatchInfo getWatchInfo] {url_str} failed to get response")
            return None

        if res.status_code not in [200, 302]:
            logger.error(f"[MissavWatchInfo getWatchInfo] {url_str} status code {res.status_code}")
            return None

        logger.info(f"[MissavWatchInfo getWatchInfo] {url_str} success")
        return self._parseWatchInfo(res.text,url_str)


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
        tasks = [ self.getSearchResults(url) for url in urls ]

        logger.info(f"[MissavSearch getSearchResultsAllPages] 共 {max_page} pages")
        result_items : List[List[ItemSearchResult]] = await limit_gather(tasks,20)
        items : List[ItemSearchResult] = []
        for result in result_items:
            if result:
                items.extend(result)

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

    async def getWatchInfo(self, url:str|URL, upload:bool = True):
        item = await self._watcher.getWatchInfo(url)
        if not item:
            logger.error(f"[MissavScraper getWatchInfo] {str(url)} failed to get watch info")
            return None

        if upload:
            await self.uploadWatchInfo(item)
        return item


    async def run(self, **kwargs):

        scrape_type = kwargs.get('scrape_type')

        if scrape_type == 'search':
            url = kwargs.get('url')
            if url:
                # items = await self._searcher.getSearchResults(url)
                search_ressult = await self._searcher.getSearchResultsAllPages(url)
            else:
                query = kwargs.get('query','露出')
                search_ressult = await self._searcher.getPostPreviews(query)

            if not search_ressult:
                logger.error(f"[MissavScraper] 搜索失败")
                self.queue.put({
                    "status": "failed",
                    "type" : "search",
                    "message": f"搜索 {url or query} 未爬取到信息"
                })
                return

            # res_list = [item.model_dump() for item in search_ressult]
            # self.queue.put({
            #     "status": "success",
            #     "type" : "search",
            #     "data":res_list,
            # })
            logger.info(f"[MissavScraper] 搜索成功, 共 {len(search_ressult)} 条数据")

            # 进一步获取信息
            search_filter = [item for item in search_ressult if item]

            items = await self.getWatchInfoFromSearch(search_filter)
            if not items:
                logger.error(f"[MissavScraper] 进一步获取信息时爬取失败")
                self.queue.put({
                    "status": "failed",
                    "type" : "search",
                    "message": f"爬取 {url or query} 失败"
                })
                return
            res_list = [item.model_dump() for item in items if item]
            logger.info(f"[MissavScraper] 进一步获取信息成功, 共 {len(res_list)} 条数据")
            self.queue.put({
                "status": "success",
                "type" : "search",
                "data":res_list,
            })
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

    async def getWatchInfoFromSearch(self, search_result : List[ItemSearchResult]) -> List[ItemWatchInfo]:
        logger.info(f"[MissavScraper] getWatchInfoFromSearch 一共 {len(search_result)} 个任务")
        tasks = [ self.getWatchInfo(item.post_url) for item in search_result ]
        return await limit_gather(tasks, 10)

    async def uploadWatchInfo(self, item:ItemWatchInfo):
        if item.releasedate is None or item.num_code is None:
            logger.error(f"[MissavScraper] {item.num_code} releasedate 或 num_code 为空")
            return

        curl_cffi.post('http://127.0.0.1:8000/missav/upload',json=item.model_dump())


    async def db_filterWithTags(self, tags:List[str]):
        filter_tag_conditions = tags
        posts = await Missav.filter(
            tags__name__in=filter_tag_conditions
            ).annotate(
                tag__count = Count('tags')
            ).filter(
                tag__count=len(filter_tag_conditions)
            )
        return posts

    async def test(self):
        items = await self._searcher.getPostPreviews('mide-565')
        if not items:
            print('no items')

        for item in items:
            print(item.title)
            print(item.post_url)
            print(item.pre_img)
            print('---')