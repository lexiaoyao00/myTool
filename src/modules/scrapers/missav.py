from ..crawler import Crawler
from typing import List
from curl_cffi import Session,Response
from core.spider import Spider
from parsel import Selector
from yarl import URL
from loguru import logger
from pydantic import BaseModel


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
    url: str
    pre_img: str

class ItemWatchInfo(BaseModel):
    pass

class MissavWatch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session


class MissavSearch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session
        self.base_url = 'https://missav.ws/cn/search'


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
                url = url,
                pre_img = pre_img
            )
            items.append(item)

        return items

    async def getPostPreviews(self,query:str):
        search_url = URL(self.base_url) / query
        # print(search_url)
        res:Response = await self.spider.asyncGet(str(search_url))
        if res is None:
            logger.error(f"[MissavSearch] {search_url} failed to get response")
            return None

        if res.status_code == 404:
            logger.error(f"[MissavSearch] {search_url} not found")
            return None

        return self._parseSearchResults(res.text)


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
            query = kwargs.get('query','')
            items = await self._searcher.getPostPreviews(query)
            if not items:
                logger.error(f"[MissavScraper] {query} not found")
                self.queue.put({
                    "status": "failed",
                    "type" : "search",
                    "message": f"搜索 {query} 未爬取到信息"
                })
                return
            # if len(items) > 2:
            #     logger.warning(f"[MissavScraper] {query} search result more than 2")
            #     self.queue.put({
            #         "status": "failed",
            #         "type" : "search",
            #         "message": f"搜索 {query} 爬取到超过2条信息,请检查番号是否正确"
            #     })
            res_list = [item.model_dump() for item in items]
            self.queue.put({
                "status": "success",
                "type" : "search",
                "data":res_list,
            })
            logger.info(f"[MissavScraper] {query} search success")
        else:
            await self.test()

    async def test(self):
        items = await self._searcher.getPostPreviews('mide-565')
        if not items:
            print('no items')

        for item in items:
            print(item.title)
            print(item.网址)
            print(item.预览图)
            print('---')