from typing import List,Optional
from pathlib import Path

from loguru import logger

from curl_cffi import Response
from parsel import Selector
from yarl import URL

from core.spider import Spider
from schemas.danbooru import ItemPostsParams, ItemTag, ItemPostInfo, ItemPostList
from ..crawler import Crawler

danbooru_header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://danbooru.donmai.us/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            }


class DanbooruPost:
    def __init__(self,spider:Spider):
        self.posts_url = "https://danbooru.donmai.us/posts"
        self.spider = spider

    def _parsePostInfo(self,text:str):
        selector = Selector(text=text)
        sel_post_info = selector.css('#post-information > ul')

        post_download_url = selector.css('#post-option-download > a::attr(href)').get()
        post_img_url = post_download_url.split('?')[0]

        post_id = sel_post_info.css('#post-info-id::text').re_first(r'\d+')

        size_type = sel_post_info.css('#post-info-size > a:nth-child(1)::text').get()
        post_size = size_type.rsplit(r'.',1)[0]
        post_file_type = size_type.rsplit(r'.',1)[1]
        post_resolution = sel_post_info.css('#post-info-size::text').re_first(r'\(.*?\)')
        post_score = sel_post_info.css('#post-info-score > span > span > a::text').get()

        sel_post_tags = selector.css('#tag-list')
        artist_tags = sel_post_tags.css('ul.artist-tag-list > li::attr(data-tag-name)').getall()
        copyrights_tags = sel_post_tags.css('ul.copyright-tag-list > li::attr(data-tag-name)').getall()
        characters_tags = sel_post_tags.css('ul.character-tag-list > li::attr(data-tag-name)').getall()
        general_tags = sel_post_tags.css('ul.general-tag-list > li::attr(data-tag-name)').getall()
        meta_tags = sel_post_tags.css('ul.meta-tag-list > li::attr(data-tag-name)').getall()

        post_info:ItemPostInfo = ItemPostInfo(id=post_id, file_url=post_img_url, download_url=post_download_url,
                                               size=post_size,file_type=post_file_type,resolution=post_resolution,
                                               score=post_score, artist_tags=artist_tags, copyrights_tags=copyrights_tags,
                                               characters_tags=characters_tags, general_tags=general_tags, meta_tags=meta_tags)

        return post_info

    def getInfoFromPost(self, url:str):
        response : Response = self.spider.syncGet(url)
        if response is None:
            return None

        return self._parsePostInfo(response.text)


    async def getInfoFromPosts(self, urls:List[str]):
        response_list : List[Response] = await self.spider.asyncGetMulties(urls)
        if response_list is None:
            return None

        post_info_list:List[ItemPostInfo] = []
        for res in response_list:
            post_info_list.append(self._parsePostInfo(res.text))

        return post_info_list

class DanbooruPage:
    def __init__(self, spider:Spider):
        self.base_url = "https://danbooru.donmai.us"
        self.spider = spider
        self.current_page = 1
        self.max_page = 0           # 0代表未知最大页数

    def _parsePageInfo(self,text:str):
        """获取页面最大页数和当前页数"""
        selector = Selector(text=text)
        current_page = selector.css('.paginator-current::text').get()
        max_page = selector.xpath('//*[@class="paginator-next"]/preceding-sibling::*[1]/text()').get()

        self.current_page = int(current_page)
        self.max_page = int(max_page) if max_page is not None else 0

    def _parsePostUrlWithPreImg(self,text:str):
        """解析页面并返回帖子链接 -> 预览图片链接的字典"""
        selector = Selector(text=text)
        post_hrefs = selector.css("div.post-preview-container > a::attr(href)").getall()
        img_urls = selector.css("div.post-preview-container picture img::attr(src)").getall()

        post_preimgs = {(self.base_url+href):img for href,img in zip(post_hrefs,img_urls)}

        return post_preimgs

    def getPost(self, url:str):
        res : Response = self.spider.syncGet(url)
        if res is None:
            return None

        return self._parsePostUrlWithPreImg(res.text)


    async def getPostsWithPreImgs(self, urls:List[str]):
        response_list : List[Response] = await self.spider.asyncGetMulties(urls)
        if response_list is None:
            return None

        post_preimg_dict = {}
        for res in response_list:
            post_preimg_dict.update(self._parsePostUrlWithPreImg(res.text))

        return post_preimg_dict

    async def getPostsWithPreImgStartPage(self, url:str, page_count:int):
        res : Response = self.spider.syncGet(url)
        if res is None:
            return None

        self._parsePageInfo(res.text)

        end_page = self.current_page + page_count - 1
        if self.max_page > 0 and end_page > self.max_page:
            end_page = self.max_page

        base_url = URL(url)
        page_urls = [str(base_url.update_query(page=page)) for page in range(self.current_page,end_page+1)]
        logger.debug(f"getPostsStartPage: {page_urls}")

        return await self.getPostsWithPreImgs(page_urls)




class DanbooruScraper(Crawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spider = Spider(
            headers = danbooru_header
        )

    async def run(self, **kwargs):
        scrape_type = kwargs.get('scrape_type')
        logger.info(f"DanbooruScraper run: {scrape_type}")
        if scrape_type is None:
            # await self.test(**kwargs)
            self.queue.put(
                {
                    "status": "error",
                    "message": "scrape_type is None"
                }
            )
            return

        if scrape_type == 'page':
            url = kwargs.get('url')
            if not url:
                self.queue.put({"status": "error", "message": "Page url is None"})
                return
            start_page = kwargs.get('start_page') or 1
            scrape_page_count = kwargs.get('scrape_page_count') or 1
            post_preimg_dict = await self.scrapePosts(url,start_page,scrape_page_count)
            res_dit = {
                "status": "success",
                "type": "page",
                "data": post_preimg_dict
            }
            self.queue.put(res_dit)
        elif scrape_type == 'post':
            url = kwargs.get('url')
            if not url:
                self.queue.put({"status": "error", "message": "Post url is None"})
                return

            item_info = self.scrapePostInfo(url)
            if item_info is not None:
                res_dit = {
                    "status": "success",
                    "type": "post",
                    "post_url": url,
                    "data": item_info.model_dump()
                }
                self.queue.put(res_dit)
            else:
                res_dit = {
                    "status": "failed",
                    "type": "post",
                }
                self.queue.put(res_dit)
        elif scrape_type == 'download':
            download_url = kwargs.get('download_url')
            download_path = kwargs.get('download_path')
            if download_url is None or download_path is None:
                self.queue.put({"status": "error", "message": "下载链接或者保存路径为空"})
                return

            save_path = await self.downloadPost(download_url, download_path)
            if save_path is None:
                self.queue.put({"status": "failed", "type": "download"})
            else:
                self.queue.put({"status": "success", "type": "download", "save_path": save_path})

        else:
            await self.test(**kwargs)


    async def test(self):
        # danbooru_page = DanbooruPage(spider=self.spider)
        # page_url = 'https://danbooru.donmai.us/'
        print("===========11111111===============")
        page_url = 'https://danbooru.donmai.us/posts?tags=order%3Arank+-censored'
        # posts = danbooru_page.getPost(url=page_url)
        posts = await self.scrapePosts(url=page_url, start_page=1,scrape_page_count=1)
        # print(posts)
        if posts is None:
            return
        # print(posts.values())
        # danbooru_post = DanbooruPost(spider=self.spider)
        post_info_list:List[ItemPostInfo] = await self.scrapeInfoFromPosts(urls=posts.keys())
        # print(post_info_list)
        post_list:ItemPostList = ItemPostList(posts=post_info_list, start_url=page_url,start_page=1, page_count=2)
        post_list.save_to_json(f'./storage/data/danbooru/test.json')

        file_url_list = [post.file_url for post in post_info_list]
        # print(file_url_list)
        print("===========222222222===============  ")

    async def scrapePostsWithParams(self, start_page:int =  1, scrape_page_count:int = 1, params:ItemPostsParams = None ):
        if params is None:
            logger.info('参数为空，默认抓取热门')
            return await self.scrapeHotPost(start_page,scrape_page_count)

        danbooru_page = DanbooruPage(self.spider)
        url = URL('https://danbooru.donmai.us/posts')
        url = url.with_query(**params.model_dump(exclude_unset=True))
        return await danbooru_page.getPostsWithPreImgStartPage(str(url),scrape_page_count)

    async def scrapePosts(self, url:str = None, start_page:int =  1, scrape_page_count:int = 1):
        if url is None:
            logger.info('参数为空，默认抓取热门')
            return await self.scrapeHotPost(start_page,scrape_page_count)

        danbooru_page = DanbooruPage(self.spider)
        page_url = URL(url)
        page_url = page_url.update_query(page=start_page)
        return await danbooru_page.getPostsWithPreImgStartPage(str(page_url),scrape_page_count)

    async def scrapeHotPost(self, start_page:int =  1, scrape_page_count:int = 1):
        danbooru_page = DanbooruPage(self.spider)
        hot_url =  URL('https://danbooru.donmai.us/posts?tags=order%3Arank+-censored')
        hot_url = hot_url.update_query(page=start_page)
        post_preimg_dict = await danbooru_page.getPostsWithPreImgStartPage(str(hot_url),scrape_page_count)

        return post_preimg_dict

    def scrapePostInfo(self, url:str):
        danbooru_post = DanbooruPost(self.spider)
        return danbooru_post.getInfoFromPost(url)

    def scrapeInfoFromPosts(self, urls:List[str]):
        danbooru_post = DanbooruPost(self.spider)
        return danbooru_post.getInfoFromPosts(urls)

    async def downloadPost(self, download_url:str, donwload_path:str):
        save_path = Path(donwload_path)

        return await self.spider.download_async(download_url, save_path)

