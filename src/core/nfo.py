from pydantic import BaseModel
from typing import List,Literal
from pathlib import Path
import xmltodict

class EmbyMovieModel(BaseModel):
    """emby 的元数据模型"""
    title : str             # 标题
    sorttitle: str          # 排序标题

    rating : float = None   # 社区评分
    criticrating : float = None  # 影评人评分

    mpaa : str = None           # 家长评级
    customrating : str = None  # 自定义评级

    plot : str = None  # 简介（概要）
    tagline : str = None  # 宣传语

    studio : List[str] = None  # 工作室
    tag: List[str] = None  # 标签
    genre : List[str] = None    # 类型

    url : str = None  # 链接


NFO_TYPE = Literal['movie','episodedetails']

class NFO:
    def save_emby_move(self, emby_movie_data: EmbyMovieModel, save_path: Path|str, nfo_type:NFO_TYPE = 'movie'):
        data = {nfo_type:emby_movie_data.model_dump(exclude_unset=True)}
        xml_str = xmltodict.unparse(data, pretty=True)

        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xml_str)



if __name__ == '__main__':
    nfo = NFO()
    emby_movie = EmbyMovieModel(
        title='title',
        sorttitle='sorttitle',
        rating=9.9,
        tagline='tagline',
        studio=['studio1', 'studio2'],
        tag=['tag1', 'tag2'],
        genre=['genre1', 'genre2']
    )
    nfo.save_emby_move(emby_movie, 'test.nfo')