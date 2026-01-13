
from ..crawler import Crawler
from core.spider import Spider
from pydantic import BaseModel,model_validator
from typing import List, Dict
from parsel import Selector
from curl_cffi import Response,Session,AsyncSession
import asyncio
import json
from pathlib import Path
import re
from string import Template
import zipfile
from core.config import PRO_DIR
from loguru import logger
from core.utils import zip_dir
import shutil


exhentai_cookies = {
    'ipb_member_id': '5663118',
    'ipb_pass_hash': '926d3a8283b0beaf3fa3d22ac5580b16',
    'igneous': 'dkb9d5u5ivd4fu1o7',
    'sk': 'ot1s9e54uuvfw7sftcz2a3nowq0l',
}

exhentai_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://exhentai.org',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

comicInfo_template = Template(
    """<?xml version="1.0" encoding="UTF-8"?>
<ComicInfo>
    <Series>$series</Series>
    <Writer>$writer</Writer>
    <Title>$title</Title>
    <Tags>$tags</Tags>
    <Web>$web</Web>
</ComicInfo>""")

# class ExHentaiTags(BaseModel):
#     language: List[str] = 'chinese'     # 语言
#     parody : List[str] = []           # 原作
#     character: List[str] = []         # 角色
#     group  : List[str] = []           # 社团
#     artist : List[str] = []           # 作者
#     female : List[str] = []         # 女性标签
#     male   : List[str] = []           # 男性标签
#     mixed   : List[str] = []           # 杂项标签
#     other : List[str] = []           # 其他标签

class ExHentaiPostModel(BaseModel):
    titile: str = ''  # 标题
    subtitle: str = ''  # 副标题
    categories: str = ''  # 分类
    uploader: str = ''  # 上传者
    Posted: str = ''  # 发布时间
    Parent: str = ''  # 父级
    Visible: str = ''  # 可见性
    Language: str = ''  # 语言
    file_size: str = ''  # 文件大小
    Length: str = ''  # 页数长度
    rate: str = ''  # 评分
    tags: Dict[str, List[str]] = {}  # 标签
    post_link: str = ''  # 帖子链接
    gid:str = None  # 帖子id
    token:str = None  # 帖子token

    # 根据post_link解析出gid和token
    # @model_validator(mode='after')
    def parse_gid_token(self):
        if self.gid is None or self.token is None:
            match = re.match(r'.*/g/(?P<gid>.*?)/(?P<token>.*?)/', self.post_link)
            if match:
                self.gid = match.group('gid')
                self.token = match.group('token')


        return self


class ExHentaiPagePost(BaseModel):
    cover:str = ''  # 封面url
    post_link:str = ''  # 帖子链接

class ExHentaiSawModel(BaseModel):
    file_name : str  # 漫画页文件名称
    view_img : str   # 观看漫画的图
    org_img : str     # 原图


class ExHentaiSaw():
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session

        self.semaphore = asyncio.Semaphore(5)  # 最多 5 个请求同时进行


    def _parse(self,html:str):
        selector = Selector(text=html)
        item = {}
        item['file_name'] = selector.css('div#i4 div:not([id])::text').get().split('::')[0].strip()
        item['view_img'] = selector.css('img#img::attr(src)').get()
        item['org_img'] = selector.css('div#i6 div:nth-child(3) a::attr(href)').get()
        if item['org_img'] is None:
            item['org_img'] = item['view_img']

        return ExHentaiSawModel(**item)

    async def getSawInfo(self,url:str):
        res:Response = await self.spider.asyncGet(url)
        if res is None:
            logger.error(f'获取漫画页面失败，url:{url}')
            return None
        if res.status_code != 200:
            logger.error(f'获取漫画页面失败，url:{url}')
            return None

        return self._parse(res.text)

    async def download_org(self,url:str,save_path:Path):
        async with self.semaphore:
            async with AsyncSession(max_clients=5) as s:
                r = await s.get(url,cookies=exhentai_cookies,headers=exhentai_headers,allow_redirects=True)
                # print("最终的 URL：", r.url)

            await self.spider.download_async(url=r.url,save_path=save_path)
            await asyncio.sleep(1)  # 等待1秒，防止请求过快



class ExHentaiPost():
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session


    def _parse_info(self,html:str):
        """解析帖子元数据"""
        # with open('test.html','w',encoding='utf-8') as f:
        #     f.write(html)
        selector = Selector(text=html)
        item = ExHentaiPostModel()
        item.titile = selector.css('h1#gn::text').get()
        item.subtitle = selector.css('h1#gj::text').get() or item.titile        # 部分画廊没有副标题
        gd3 = selector.css('div#gmid div#gd3')
        item.categories = gd3.css('div#gdc div::text').get()
        item.uploader = gd3.css('div#gdn a::text').get()
        gdd = gd3.css('div#gdd tr')
        item.Posted = gdd[0].css('td.gdt2::text').get()
        item.Parent = gdd[1].css('td.gdt2::text').get()
        item.Visible = gdd[2].css('td.gdt2::text').get()
        item.Language = gdd[3].css('td.gdt2::text').get().strip()
        item.file_size = gdd[4].css('td.gdt2::text').get()
        item.Length = gdd[5].css('td.gdt2::text').get()

        item.rate = gd3.css('div#gdr td#rating_label::text').get()
        #taglist > table > tbody > tr:nth-child(1)
        taglist_tr = selector.css('#taglist > table  tr')
        # print(taglist)
        for tags in taglist_tr:
            tag_type = tags.css('td.tc::text').get()
            tag_list = tags.css('div a::text').getall()
            item.tags[tag_type] = tag_list

        item.post_link = selector.css('table.ptt a::attr(href)').get()

        item.parse_gid_token()
        return item

    def _parse_saw_url(self,html:str,saw_url_list_output:List[str]):
        """解析查看漫画页面的URL"""
        selector = Selector(text=html)
        saw_urls = selector.css('div#gdt a::attr(href)').getall()
        saw_url_list_output.extend(saw_urls)


    def _parse_post_pages(self,html:str):
        selector = Selector(text=html)
        last_page_url = selector.css('table.ptt td:nth-last-child(2) a::attr(href)').get()
        match = re.match(r'(?P<base_ulr>.*)?p=(?P<page>\d+)', last_page_url)
        if match:
            last_page_num = int(match.group('page'))
            base_url = match.group('base_ulr')

            post_pages = [f'{base_url}p={i}' for i in range(0,last_page_num+1)]
            return post_pages

        return None




    async def getPostInfo(self,url:str):
        res : Response = await self.spider.asyncGet(url=url)
        if res.status_code != 200:
            return None

        return self._parse_info(res.text)


    async def getSawUrlList(self,url:str):
        res : Response = await self.spider.asyncGet(url=url)
        if res and res.status_code != 200:
            return None

        post_pages = self._parse_post_pages(res.text)
        if post_pages is None:
            return [url]

        res_pages = await self.spider.asyncGetMulties(urls=post_pages,max_workers=5)

        saw_url_list_output:List[str] = []
        for res in res_pages:
            if res is None:
                continue
            self._parse_saw_url(res.text,saw_url_list_output)
        return saw_url_list_output

class ExHentaiPage():
    def __init__(self,spider:Spider,session:Session):
        self.spider = spider
        self.session = session


    def _parse_info(self,html:str):
        selector = Selector(text=html)
        post_list = selector.css('div.itg.gld div.gl1t div.gl3t > a::attr(href)').getall()


        return post_list

    def _parse_next_page(self,html:str):
        selector = Selector(text=html)
        next_page = selector.css('a#dnext::attr(href)').get()
        return next_page


    async def getPostList(self,url:str):
        res : Response = await self.spider.asyncGet(url=url)
        if res is None:
            print('抓取失败：res is None')
            return None

        if res.status_code != 200:
            print('抓取失败：code ', res.status_code)
            return None

        post_list = self._parse_info(res.text)
        return post_list

    async def getPageList(self,url:str, page_max:int = 0):
        page_urls = [url]
        res : Response = await self.spider.asyncGet(url=url)
        if res is None:
            print(f'抓取 "{url}" 失败：res is None')
            return None

        if res.status_code != 200:
            print(f'抓取 "{url}" 失败：code ', res.status_code)
            return None


        next_page = self._parse_next_page(res.text)
        if next_page is None:
            return page_urls

        page_urls.append(next_page)

        while page_max == 0 or len(page_urls) < page_max:
            res : Response = await self.spider.asyncGet(url=next_page)
            if res is None:
                print(f'抓取 "{next_page}" 失败：res is None')
                return None

            if res.status_code != 200:
                print(f'抓取 "{next_page}" 失败：code ', res.status_code)
                return None

            next_page = self._parse_next_page(res.text)
            if next_page is None:
                break

            page_urls.append(next_page)

        return page_urls


        # if next_page:
        #     next_page_list = await self.getPostList(url=next_page)

class ExHentaiScraper(Crawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = Session()
        self.spider = Spider(headers=exhentai_headers, cookies=exhentai_cookies)

        self.exhentai_post = ExHentaiPost(spider=self.spider,session=self.session)
        self.exhentai_page = ExHentaiPage(spider=self.spider,session=self.session)
        self.exhentai_saw = ExHentaiSaw(spider=self.spider,session=self.session)

        self._data_save_dir = PRO_DIR / Path('storage/data/exhentai')
        self._download_save_dir = PRO_DIR / Path('storage/download/exhentai')
        self._item_save_path = self._data_save_dir / 'item.json'
        self._saved_items = {}


        self.init()

    def init(self):
        if self._item_save_path.exists():
            with open(self._item_save_path,'r',encoding='utf-8') as f:
                self._saved_items = json.load(f)

    def save_items(self):
        with open(self._item_save_path,'w',encoding='utf-8') as f:
            json.dump(self._saved_items,f,ensure_ascii=False,indent=4)

    def comicInfo_to_cbz(self, comicInfo_content:str,cbz_path:str|Path):
        cbz_path = Path(cbz_path)

        with zipfile.ZipFile(cbz_path, 'r') as zin:
            has_comicinfo = any(item.filename == "ComicInfo.xml" for item in zin.infolist())

        if not has_comicinfo:
            # 没有 ComicInfo.xml，直接追加
            mode_data = comicInfo_content
            if isinstance(mode_data, str):
                mode_data = mode_data.encode("utf-8")  # 确保写入的是 bytes
            with zipfile.ZipFile(cbz_path, 'a') as zout:
                zout.writestr("ComicInfo.xml", mode_data)
            logger.info(f"已向 {cbz_path} 添加 ComicInfo.xml")

        else:
            # 有 ComicInfo.xml，需要重建压缩包进行替换
            tmp_path = cbz_path.with_suffix(".tmp")
            with zipfile.ZipFile(cbz_path, 'r') as zin, \
                zipfile.ZipFile(tmp_path, 'w') as zout:
                for item in zin.infolist():
                    if item.filename != "ComicInfo.xml":
                        filedata = zin.read(item.filename)
                        zout.writestr(item, filedata)
                # 写入新的 ComicInfo.xml
                mode_data = comicInfo_content
                if isinstance(mode_data, str):
                    mode_data = mode_data.encode("utf-8")
                zout.writestr("ComicInfo.xml", mode_data)
            shutil.move(tmp_path, cbz_path)
            logger.info(f"{cbz_path} 的 ComicInfo.xml 已替换")

    def _glob_cbz(self, cbz_dir:Path, recursive:bool = True):
        if recursive:
            files = cbz_dir.rglob('*.cbz')
        else:
            files =cbz_dir.glob('*.cbz')

        res = [file for file in files if file.is_file()]
        return res

    def add_metadata_to_cbz(self,cbz_dir:Path,recursive:bool = True):
        cbz_list = self._glob_cbz(cbz_dir,recursive=recursive)
        files_stem =  [cbz.stem for cbz in cbz_list]
        # print(files_stem)
        logger.info(f'找到 {len(cbz_list)} 个 cbz 文件')

        # 文件名中不会有 '/' 符号，替换成 ' '
        cache_items_subtitle = {item['subtitle'].replace('/',' '):item['gid'] for item in self._saved_items.values()}

        failed : List[str] = []
        for file_stem in files_stem:
            if file_stem in cache_items_subtitle.keys():
                logger.info(f'找到 {file_stem}')
                # item = cache_items_subtitle.index(file_stem)
                gid = cache_items_subtitle[file_stem]

                comicInfo_file = self._data_save_dir / f'ComicInfo/ComicInfo_{gid}.xml'
                logger.info(f'对应的 ComicInfo 文件为：{comicInfo_file}')
                if comicInfo_file.exists():
                    with open(comicInfo_file,'r',encoding='utf-8') as f:
                        comicInfo_content = f.read()
                    self.comicInfo_to_cbz(comicInfo_content,cbz_list[files_stem.index(file_stem)])
                    logger.info(f'成功添加 {file_stem} 的 ComicInfo 文件')
                else:
                    logger.error(f'未找到 {file_stem} 的 ComicInfo 文件')
                    failed.append(file_stem)
            else:
                logger.error(f'未找到 {file_stem} 的信息')
                failed.append(file_stem)

        logger.info(f'添加完成，共 {len(cbz_list)} 个文件，{len(failed)} 个文件添加失败')
        return failed

    def _to_comicInfo(self,post_data: ExHentaiPostModel, save_to_path:bool = False, save_path:Path|str = None):
            tags_list = []
            for _,tags in post_data.tags.items():
                tags_list.extend(tags)
            tags_str = ','.join(tags_list)
            artist_list = post_data.tags.get('artist:')
            if artist_list:
                artist_str = ','.join(post_data.tags.get('artist:'))
                series_str = artist_str
            else:
                artist_str = 'Unknown'
                series_str = post_data.subtitle or ''
            data = {
                'series': series_str,
                'writer': artist_str,
                'title': post_data.titile,
                'tags': tags_str,
                'web': post_data.post_link,
            }
            coentent = comicInfo_template.substitute(data)

            if not save_to_path :
                return coentent

            path = save_path or self._data_save_dir /  f'ComicInfo/ComicInfo_{post_data.gid}.xml'
            with open(path,'w',encoding='utf-8') as f:
                f.write(coentent)

            return str(path)


    async def run(self,**kwargs):
        scrape_type = kwargs.get('scrape_type')


        if scrape_type == 'saw':
            url = kwargs.get('url') or 'https://exhentai.org/s/056ae2c3ff/3595060-1'
            saw_info = await self.exhentai_saw.getSawInfo(url=url)
            print(saw_info.model_dump())

        elif scrape_type == 'post':
            # url = 'https://exhentai.org/fullimg/3595060/1/4doy5ufaivh/01_1.jpg'
            # await self.exhentai_saw.download_org(url=url,save_path=self._download_save_dir / 'test.jpg')

            url = kwargs.get('url') or 'https://exhentai.org/g/3595060/f35f231103/'
            post_item = await self.exhentai_post.getPostInfo(url=url)
            print(post_item.model_dump())
            saw_urls = await self.exhentai_post.getSawUrlList(url=url)
            print(saw_urls)
            tasks = [self.exhentai_saw.getSawInfo(url=saw_url) for saw_url in saw_urls]
            saw_infos = await asyncio.gather(*tasks)
            if saw_infos is None:
                return

            # path = self._data_save_dir / 'saw.json'
            # with open(path,'w',encoding='utf-8') as f:
            #     json.dump([saw_info.model_dump() for saw_info in saw_infos],f,ensure_ascii=False,indent=4)

            download_dir = self._download_save_dir / post_item.subtitle
            # download_tasks = [self.exhentai_saw.download_org(url=info.org_img,save_path= download_dir / info.file_name) for info in saw_infos if info is not None]
            # await asyncio.gather(*download_tasks)
            self._to_comicInfo(post_item,save_to_path=True,save_path=download_dir / 'ComicInfo.xml')

            # zip_dir(download_dir, download_dir.with_suffix('.cbz'))



        elif scrape_type == 'page':
            url = kwargs.get('url') or 'https://exhentai.org/favorites.php?favcat=6'
            page_list = await self.exhentai_page.getPageList(url=url,page_max=0)

            print(page_list)
            tasks = [self.exhentai_page.getPostList(url=url) for url in page_list]
            post_list = await asyncio.gather(*tasks)
            # print(post_list)
            post_list = [post_url for sub_list in post_list for post_url in sub_list]
            print(post_list)
            print('长度：',len(post_list))
            # if post_list is None:
            #     return

            tasks = [self.exhentai_post.getPostInfo(url=post_url) for post_url in post_list]
            post_items = await asyncio.gather(*tasks)
            for post_item in post_items:
                if post_item is None:
                    continue
                self._to_comicInfo(post_item,save_to_path=True)
                self._saved_items.update({post_item.gid:post_item.model_dump()})

            self.save_items()
            print('保存成功')

        elif scrape_type == 'metadata':
            self.add_metadata_to_cbz(cbz_dir=PRO_DIR / Path('storage/data/exhentai/manga_tmp'))
        else:
            print('未知的爬取类别')


        print('爬取结束')