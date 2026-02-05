from pydantic import BaseModel,model_validator
from typing import List, Dict
import re


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