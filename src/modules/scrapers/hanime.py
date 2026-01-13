from typing import List,Dict,Optional,ClassVar
import json
import asyncio

from loguru import logger
from curl_cffi import Response,Session
from pydantic import BaseModel,model_validator
from core.spider import Spider
from parsel import Selector
from yarl import URL
from pathlib import Path
import time
from core.config import PRO_DIR
from core.nfo import NFO, EmbyMovieModel
import re

from ..crawler import Crawler



hanime_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.170"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.170", "Chromium";v="143.0.7499.170", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

hanime_cookie = {
    # 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IlwvUG91V2NmNTRuSXl2NEtKek9aQ0F3PT0iLCJ2YWx1ZSI6Iks4R3FUekdCVHZwVjREYnkrUUFYY2NyNm9iaUszditPOGp5ME1OTm16WTJXSTRLekNkVEU0bkM1aDlmbXlLOGsrOEthRUYzY1A2bmp0OTFYeEsxM2lCMTl6VGh0NThuZnRvUzFXK2hjSlQ1eTFRYllmVzgxTU5pK1E4OGx3cE1CRmZIekFzVnZvY0VCZzJmNFRZb041U3BoU0poNHZuWm5qeEpNUDhMTDdFQllFakg0MDV5Y0xQXC84TjM3SEgzeHkiLCJtYWMiOiJjMzY0YWE0NzhmNWZkOTRhYjYwYzc0NzBhYzUwYmRjMWQ1YjQ0ZWNhOWQ2YjQzMWU5Mjg3YWNiZjExZjRkMWVkIn0%3D',
    # '_ga_2JNTSFQYRQ': 'deleted',
    # '_gid': 'GA1.2.675969733.1767579163',
    # 'cf_clearance': 'id89XEJkb_g93ezkdhIIfu2mOqU6noJLyJyfHiFizLE-1767579309-1.2.1.1-5n.CNVpZLhPAw.tmcuzI_OSRvi90VvVJKSq69Bb9ZOLcaSEU7GVrsGXeKspV3dCKwuYP.PN_.sE20X5C4_cddnLIcR2T8ku20t7GwQZV2XWaJxsv6fbvQqxfnQXT634.q8iO6rC7XndtP5CzfCGTMJegYaFBDGVbwQsZkolA1SzuyCxD5_aUs.FLfnya7c5UBXthmcwYKxmKoPhiwC0OuxLOcDAMkhgY5aXx_uHPrZpRj0NkJrgZBbrBgOLqDtP3',
    # 'XSRF-TOKEN': 'eyJpdiI6IkpWMHlySTVLQWNZVU8xSUFpbFhCb0E9PSIsInZhbHVlIjoiU283N3lIbEhuTFdhcXRZOVFGUmJSS1o4Y01LTVFVck5NbXVveTNFbFB3VWlMNHE4UEJkbHlIWDh4N3p3ZEJiMiIsIm1hYyI6IjUxMDE1ZDBjMjk1MmIyNWUyYWY3MGU5MGM0ZDcwOWJjZWVjNWJlMDQ5NGU2ZTZkZjAzYjYyYzI3NjU4ODFmMjYifQ%3D%3D',
    # 'hanime1_session': 'eyJpdiI6IkRVcjJWaDBxcG10SGtsZjRHTVZaUFE9PSIsInZhbHVlIjoiTnBjenpSMWxjZzJqWHFxaHA4dnBpbTFlY2tvVVpRcUx3R0JqQnh6d2RCREtJWkFrWFFSc3ZzXC91bDJudzFPWUQiLCJtYWMiOiJhZjUyOWY3Y2ViZGQzNTUyNjkxZjJmYTI0NTg0NmZmMzQ4MmNjZDU3NzIyNThkNWFhYWI3ODMwZTdlMjU4NmFmIn0%3D',
    '_ga': 'GA1.2.120883284.1751720600',
    '_gat_gtag_UA_125786247_2': '1',
}


class ItemSearchParameters(BaseModel):
    query : str = None
    type : str = None
    genre : str = '全部'
    tags : List[str] = None
    sort : str = None
    date : str = None
    duration : str = None
    page : int = 1

    # 字段到URL参数名的映射（需要列表展开时使用）
    FIELD_NAME_MAP : ClassVar[Dict[str, str]]= {
        "tags": "tags[]"
    }

    def to_query_list(self, **kwargs) -> list[tuple[str, str]]:
        """
        转换为 yarl 可用的查询列表。
        支持 model_dump() 的所有参数，例如：
        exclude_none=True, exclude_unset=True, exclude_defaults=True
        """
        # 直接传递 kwargs 给 model_dump
        data = self.model_dump(**kwargs)

        query_list: list[tuple[str, str]] = []
        for field_name, value in data.items():
            param_name = self.FIELD_NAME_MAP.get(field_name, field_name)
            if isinstance(value, list):
                for v in value:
                    query_list.append((param_name, str(v)))
            else:
                query_list.append((param_name, str(value)))
        return query_list


class ItemPlaylist(BaseModel):
    title : str
    playlist_urls : List[str]

class ItemSearchPreview(BaseModel):
    title : str
    watch_url : str
    pre_img : str
    anime_id : str = None

    @model_validator(mode='after')
    def set_anime_id(self):
        self.anime_id = URL(self.watch_url).query.get('v')
        return self



class ItemWatchInfo(BaseModel):
    url : str
    artist : str
    category : str
    upload_time : str
    title : str
    description : str
    tags : List[str] = None
    download_urls : Dict[str,str] = None

    playlist : Optional[ItemPlaylist] = None


class HAnimeWatch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session

    def _parse_download_page(self,download_page_url:str):
        if not download_page_url:
            return None

        response : Response = self.spider.syncGet(url=download_page_url,session=self.session)
        if response is None:
            logger.warning(f'hanime _parse_download response is None')
            return None

        selector = Selector(text=response.text)
        download_table = selector.css('table.download-table')
        trs = download_table.css('tr')[1:]     # 跳过表头
        size_list = trs.css('td:nth-child(2)::text').getall()
        download_urls = trs.css('td:nth-last-child(1) a::attr(data-url)').getall()

        size_list = [re.search(r'\d+',size_str).group(0) for size_str in size_list]

        # print(download_urls)
        # print(size_list)

        return {str(size):url for size,url in zip(size_list,download_urls)}


    def _parseWatchInfo(self,html:str,parse_playlist:bool=True):
        selector = Selector(text=html)
        item = {}

        item['url'] = selector.css('link[rel="canonical"]::attr(href)').get()

        # logger.debug(f'item url: {item["url"]}')
        if not item['url']:
            return None

        video_urls = selector.css('video source::attr(src)').getall()
        video_urls_size = selector.css('video source::attr(size)').getall()

        # print(video_urls)
        # print(video_urls_size)
        if video_urls:
            item['download_urls'] = {str(size):url for size,url in zip(video_urls_size,video_urls)}
        # print(watch_urls)
        else:
            download_page_url = selector.css('a#downloadBtn::attr(href)').get()
            item['download_urls'] = self._parse_download_page(download_page_url)



        item['artist'] = selector.css('a#video-artist-name::text').get(default='').strip()
        item['category'] = selector.css('a#video-artist-name + a::text').get(default='').strip()


        # video_details_wrapper = selector.css('div.video-details-wrapper')[0]
        video_details_wrapper = selector.xpath('//div[normalize-space(@class)="video-details-wrapper"]')[0]
        item['upload_time'] = video_details_wrapper.css('div.hidden-xs::text').get(default='').strip().split()[-1]
        item['title'] = video_details_wrapper.css('div.video-description-panel > div:not([class])::text').get()
        item['description'] = video_details_wrapper.css('div.video-description-panel > div.video-caption-text.caption-ellipsis::text').get(default='').replace('\r\n','').strip()

        video_tags_wrapper = selector.css('div.video-tags-wrapper')[0]
        single_video_tags = video_tags_wrapper.css('div.single-video-tag a:not([data-target])::text').getall()
        item['tags'] = [tag.strip() for tag in single_video_tags]

        if not parse_playlist:
            return ItemWatchInfo(**item)

        playlist_wrapper = selector.css('div#video-playlist-wrapper')[0]
        if not playlist_wrapper:
            return ItemWatchInfo(**item)

        playlist_title = playlist_wrapper.css('h4::text').get().strip()
        playlist_urls = playlist_wrapper.css('div.related-watch-wrap.multiple-link-wrapper a.overlay::attr(href)').getall()
        item['playlist'] = ItemPlaylist(title=playlist_title,playlist_urls=playlist_urls)

        return ItemWatchInfo(**item)


    def getWatchInfo(self,url:str):
        response : Response = self.spider.syncGet(url=url,session=self.session)
        if response is None:
            logger.warning(f'hanime getWatchInfo response is None')
            return None

        return self._parseWatchInfo(html=response.text)

    async def getSeriesWatchInfos(self,url:str):
        response : Response = self.spider.syncGet(url=url,session=self.session)
        if response is None:
            logger.warning(f'hanime getSeriesWatchInfo url:{url} response is None')
            return None

        if response.status_code not in [200,400]:
            logger.warning(f'hanime getSeriesWatchInfo url:{url} response status is {response.status_code}')
            return None

        watch_info : ItemWatchInfo = self._parseWatchInfo(html=response.text)
        if watch_info is None or watch_info.playlist is None or len(watch_info.playlist.playlist_urls) < 2:
            return [watch_info]

        series_res = await self.spider.asyncGetMulties(urls=watch_info.playlist.playlist_urls)
        if series_res is None:
            return None

        post_info_list : List[ItemWatchInfo] = [self._parseWatchInfo(html=res.text) for res in series_res]

        return post_info_list

class HAnimeSearch:
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session
        self.base_url = 'https://hanime1.me/search'

        self.css_sel1 = '#home-rows-wrapper > div.home-rows-videos-wrapper > a:not([target])'
        self.css_sel2 = '#home-rows-wrapper > div.content-padding-new > div.row.no-gutter div.hidden-xs[title]'


    def _parseWatchPreviews2(self,selector:Selector):
        watch_sels = selector.css(self.css_sel2)

        if not watch_sels:
            logger.warning('hanime _parseWatchPreviews2 watch_sels2 is None')
            return None

        urls = watch_sels.css('a.overlay::attr(href)').getall()
        titles = watch_sels.css('::attr(title)').getall()
        pre_imgs = watch_sels.css('img[loading]::attr(src)').getall()

        return [ItemSearchPreview(title=title,watch_url=url,pre_img=pre_img) for title,url,pre_img in zip(titles,urls,pre_imgs)]


    def _parseWatchPreviews(self,html:str):
        selector = Selector(text=html)
        watch_sels = selector.css(self.css_sel1)

        if not watch_sels:
            logger.warning('hanime _parseWatchPreviews watch_sels1 is None, try css_sel2')
            return self._parseWatchPreviews2(selector)

        urls = watch_sels.css('::attr(href)').getall()
        titles = watch_sels.css('div.home-rows-videos-title::text').getall()
        pre_imgs = watch_sels.css('img::attr(src)').getall()

        return [ItemSearchPreview(title=title,watch_url=url,pre_img=pre_img) for title,url,pre_img in zip(titles,urls,pre_imgs)]


    def getWatchPreview(self,url:str):
        response : Response = self.spider.syncGet(url=url,session=self.session)
        # print(response.text)
        if response is None:
            logger.warning('hanime getWatchPreview response is None')
            return None

        return self._parseWatchPreviews(html=response.text)

    def getWatchPreviewWithParams(self,parameters:ItemSearchParameters = None):
        url = URL(self.base_url)
        if parameters is not None:
            url = url.with_query(parameters.to_query_list(exclude_unset=True))
        logger.info(f'HAnimeSearch getWatchPreviewWithParams url: {url}')
        return self.getWatchPreview(url=str(url))



class HAnimeScraper(Crawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = Session()
        self.spider = Spider(
            headers = hanime_headers,
            cookies = hanime_cookie
        )

        self.searcher = HAnimeSearch(self.spider,session=self.session)
        self.watch = HAnimeWatch(self.spider,session=self.session)

        self.nfo = NFO()

    async def run(self,**kwargs):
        scrape_type = kwargs.get('scrape_type')

        if scrape_type == 'search':
            url = kwargs.get('url')
            if not url:
                logger.warning('hanime run watch url is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "watch",
                    "message": "url is None"
                })
                return

            item_pre_list = self.searchPreviews(url=url)
            if item_pre_list is None:
                logger.warning('hanime run item_pre_list is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "search",
                    "message": "抓取到的数据为空"
                })
                return

            res_list = [item.model_dump() for item in item_pre_list]
            # 保存数据测试
            save_path = PRO_DIR / 'storage/data/hanime/search.json'
            save_path.parent.mkdir(parents=True,exist_ok=True)
            with open(save_path,'w',encoding='utf-8') as f:
                f.write(json.dumps(res_list,ensure_ascii=False,indent=4))

            self.queue.put({
                "status": "success",
                "type" : "search",
                "data": res_list
            })

        elif scrape_type == 'watch':
            url = kwargs.get('url')
            download_flag = kwargs.get('download',False)
            if not url:
                logger.warning('hanime run watch url is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "watch",
                    "message": "url is None"
                })
                return
            logger.info(f'HAnimeScraper run watch url: {url}')
            watch_info = self.getWatchInfo(url=url)
            if watch_info is None:
                logger.warning('hanime run watch_info is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "watch",
                    "message": "抓取到的数据为空"
                })
                return

            # save_path = PRO_DIR / 'storage/data/hanime/watch.json'
            # save_path.parent.mkdir(parents=True,exist_ok=True)
            # with open(save_path,'w',encoding='utf-8') as f:
            #     f.write(json.dumps(watch_info.model_dump(),ensure_ascii=False,indent=4))

            download_dict : Dict[str,str] = {}
            if watch_info.playlist:
                series_titile = watch_info.playlist.title
            else:
                series_titile = watch_info.title
            series_titile = re.sub(r'[\\/:*?"<>|]', ' ', series_titile)

            file_stem = watch_info.title
            file_stem = re.sub(r'[\\/:*?"<>|]', ' ', file_stem)
            path = PRO_DIR / f'storage/data/hanime/nfo/{series_titile}/{file_stem}.nfo'
            self._save_to_nfo(watch_info=watch_info,save_path=path)

            if download_flag:
                if watch_info.download_urls is None or len(watch_info.download_urls) == 0:
                    logger.warning(f'{watch_info.title} download_urls is None or empty: {watch_info.model_dump(exclude_unset=True)}')
                    self.queue.put({
                        "status": "failed",
                        "type" : "watch",
                        "message": "下载链接为空"
                    })
                else:
                    max_resolution = max(list(watch_info.download_urls.keys()),key=int)
                    download_url = watch_info.download_urls[max_resolution]
                    file_suffix = download_url.split('.')[-1].split('?')[0]
                    file_name = f'{file_stem}.{file_suffix}'
                    download_dict[file_name] =download_url

                    logger.info(f'开始下载 "{watch_info.title}" 视频文件')
                    await self._download(download_dict=download_dict,series_name=series_titile)

            self.queue.put({
                "status": "success",
                "type" : "watch",
                "data": watch_info.model_dump(exclude_unset=True)
            })

        elif scrape_type == 'series':
            url = kwargs.get('url')
            download_flag = kwargs.get('isdownload',False)
            if not url:
                logger.warning('hanime run series url is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "series",
                    "message": "url is None"
                })
                return

            watch_info_list = await self.watch.getSeriesWatchInfos(url=url)
            if watch_info_list is None:
                logger.warning('hanime run watch_info_list is None')
                self.queue.put({
                    "status": "failed",
                    "type" : "series",
                    "message": "抓取到的数据为空"
                })
                return

            # return watch_info_list

            download_dict : Dict[str,str] = {}
            if watch_info_list[0].playlist:
                series_titile = watch_info_list[0].playlist.title
            else:
                series_titile = watch_info_list[0].title
            series_titile = re.sub(r'[\\/:*?"<>|]', ' ', series_titile)

            for watch_info in watch_info_list:
                file_stem = watch_info.title
                file_stem = re.sub(r'[\\/:*?"<>|]', ' ', file_stem)
                path = PRO_DIR / f'storage/data/hanime/nfo/{series_titile}/{file_stem}.nfo'
                self._save_to_nfo(watch_info=watch_info,save_path=path)


                if watch_info.download_urls is None or len(watch_info.download_urls) == 0:
                    logger.warning(f'{watch_info.title} download_urls is None or empty:{watch_info.model_dump(exclude_unset=True)}')
                    continue

                max_resolution = max(list(watch_info.download_urls.keys()),key=int)
                download_url = watch_info.download_urls[max_resolution]
                file_suffix = download_url.split('.')[-1].split('?')[0]
                file_name = f'{file_stem}.{file_suffix}'
                download_dict[file_name] =download_url


            if download_flag:
                logger.info(f'开始下载 "{series_titile}" 系列视频')
                await self._download(download_dict=download_dict,series_name=series_titile)

            # print(download_dict)

        else:
            await self.test()



    async def _download(self, download_dict:Dict[str,str], series_name:str = None):

        download_dir = PRO_DIR / 'storage/download/hanime'
        if series_name:
            download_dir = download_dir / series_name
        download_tasks = []
        download_progress = {}

        def on_download_progress(name, downloaded, total):
            percent = downloaded / total
            download_progress[name] = percent

            self.queue.put({
                "status": "running",
                "type" : "downloading",
                "progress": download_progress

            })

        for file_name, download_url in download_dict.items():
            file_path = download_dir / file_name
            download_tasks.append(self.spider.download_async(url=download_url, save_path=file_path,on_progress=on_download_progress,name=file_name))



        self.queue.put({
                "status": "running",
                "type" : "download_start",
                "message": "开始下载",
                "data": list(download_dict.keys())
            })
        await asyncio.gather(*download_tasks)
        self.queue.put({
                "status": "running",
                "type" : "download_end",
                "message": "下载完成"
            })


    def _save_to_nfo(self,watch_info:ItemWatchInfo, save_path:Path|str = None):
        model_data = {
            "title": watch_info.title,
            "sorttitle": watch_info.title,
            "plot": watch_info.description,
            "studio": [watch_info.artist],
            "tag": watch_info.tags,
            "genre": [watch_info.category],
            "url": watch_info.url
        }
        emby_nfo : EmbyMovieModel = EmbyMovieModel(**model_data)

        file_stem = watch_info.title
        # 处理文件名中的特殊字符
        file_stem = re.sub(r'[\\/:*?"<>|]', ' ', file_stem)
        path = save_path or PRO_DIR / f'storage/data/hanime/nfo/{file_stem}.nfo'
        path.parent.mkdir(parents=True,exist_ok=True)

        self.nfo.save_emby_move(emby_nfo,save_path=path)
        logger.info(f'HAnimeScraper _save_to_nfo save_path: {path}')
        return path


    def searchPreviews(self, url:str):
        return self.searcher.getWatchPreview(url=url)

    def searchPreviewsWithParameters(self, parameters:ItemSearchParameters = None):
        return self.searcher.getWatchPreviewWithParams(parameters=parameters)

    def getWatchInfo(self,url:str):
        return self.watch.getWatchInfo(url=url)

    async def getSeriesWatchInfos(self,url:str):
        return await self.watch.getSeriesWatchInfos(url=url)

    async def test(self):
        # url = URL('https://hanime1.me/search')
        # # url = url.update_query({"genre":"裏番"})
        # url = url.update_query({"genre":"3D動畫"})
        # print(f'url: {url}')
        # item_pre_list = scraper.searchPreviews(url=str(url))


        # params = ItemSearchParameters(genre="裏番",query='雷火劍')
        # params = ItemSearchParameters(query='武田弘光',tags=['碧池','痴女','公眾場合'])
        params = ItemSearchParameters(query='雷火劍',tags=['碧池','痴女','公眾場合'])
        item_pre_list = self.searchPreviewsWithParameters(parameters=params)

        if not item_pre_list:
            print('hanime searchPreviews is None')
            return

        pre_list = [item_pre.model_dump() for item_pre in item_pre_list]
        # print(pre_list)
        file_name_part = params.model_dump(exclude_unset=True,exclude={'tags'}).values()
        file_name =  '_'.join(file_name_part)
        if params.tags:
            for tag in params.tags:
                file_name += f'_{tag}'
        save_path = Path(f'storage/data/hanime/page_{file_name}.json')
        save_path.parent.mkdir(parents=True,exist_ok=True)

        with open(str(save_path),'w',encoding='utf-8') as f:
            json.dump(pre_list, f, ensure_ascii=False, indent=4)


        # idx = 11
        # item = item_pre_list[idx]

        scraped_urls:List[str] = []
        for idx,item in enumerate(item_pre_list):
            url = item.watch_url
            if url in scraped_urls:
                logger.debug(f'url: {url} 已经爬取过了，跳过')
                continue

            serises = await self.getSeriesWatchInfos(url=url)

            if serises is None:
                return

            serises_title:str = None
            if isinstance(serises,list):
                scraped_urls.extend([serise.url for serise in serises])
                serises_title = serises[0].playlist.title
                serises_dict = [serise.model_dump(exclude=['playlist']) for serise in serises]
            else:
                scraped_urls.append(serises.url)
                serises_title = serises.title
                serises_dict = serises.model_dump()

            if serises_title is None:
                serises_title = 'Unknown'

            logger.info(f'系列名称: {serises_title}')
            file_name = serises_title.split('/')[0]
            logger.info(f'系列名称保存的文件名: {file_name}')
            save_path = Path(f'storage/data/hanime/{file_name}.json')
            save_path.parent.mkdir(parents=True,exist_ok=True)
            logger.info(f'save_path: {save_path}')

            with open(str(save_path),'w',encoding='utf-8') as f:
                json.dump(serises_dict, f, ensure_ascii=False, indent=4)

            time.sleep(1)       # 防止过快导致429


async def testHAnime():
    scraper = HAnimeScraper()

    # url = URL('https://hanime1.me/search')
    # # url = url.update_query({"genre":"裏番"})
    # url = url.update_query({"genre":"3D動畫"})
    # print(f'url: {url}')
    # item_pre_list = scraper.searchPreviews(url=str(url))


    # params = ItemSearchParameters(genre="裏番",query='雷火劍')
    # params = ItemSearchParameters(query='武田弘光',tags=['碧池','痴女','公眾場合'])
    params = ItemSearchParameters(query='雷火劍',tags=['碧池','痴女','公眾場合'])
    item_pre_list = scraper.searchPreviewsWithParameters(parameters=params)

    if not item_pre_list:
        print('hanime searchPreviews is None')
        return

    pre_list = [item_pre.model_dump() for item_pre in item_pre_list]
    # print(pre_list)
    file_name_part = params.model_dump(exclude_unset=True,exclude={'tags'}).values()
    file_name =  '_'.join(file_name_part)
    if params.tags:
        for tag in params.tags:
            file_name += f'_{tag}'
    save_path = Path(f'storage/data/hanime/page_{file_name}.json')
    save_path.parent.mkdir(parents=True,exist_ok=True)

    with open(str(save_path),'w',encoding='utf-8') as f:
        json.dump(pre_list, f, ensure_ascii=False, indent=4)


    # idx = 11
    # item = item_pre_list[idx]

    scraped_urls:List[str] = []
    for idx,item in enumerate(item_pre_list):
        url = item.watch_url
        if url in scraped_urls:
            logger.debug(f'url: {url} 已经爬取过了，跳过')
            continue

        serises = await scraper.getSeriesWatchInfos(url=url)

        if serises is None:
            return

        serises_title:str = None
        if isinstance(serises,list):
            scraped_urls.extend([serise.url for serise in serises])
            serises_title = serises[0].playlist.title
            serises_dict = [serise.model_dump(exclude=['playlist']) for serise in serises]
        else:
            scraped_urls.append(serises.url)
            serises_title = serises.title
            serises_dict = serises.model_dump()

        if serises_title is None:
            serises_title = 'Unknown'

        logger.info(f'系列名称: {serises_title}')
        file_name = serises_title.split('/')[0]
        logger.info(f'系列名称保存的文件名: {file_name}')
        save_path = Path(f'storage/data/hanime/{file_name}.json')
        save_path.parent.mkdir(parents=True,exist_ok=True)
        logger.info(f'save_path: {save_path}')

        with open(str(save_path),'w',encoding='utf-8') as f:
            json.dump(serises_dict, f, ensure_ascii=False, indent=4)

        time.sleep(1)       # 防止过快导致429


