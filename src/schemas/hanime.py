from pydantic import BaseModel,model_validator
from typing import List,Dict,Optional,ClassVar
from yarl import URL



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

