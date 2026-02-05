from pydantic import BaseModel,model_validator
from typing import List,Optional
from itertools import chain
from pathlib import Path


class ItemPostsParams(BaseModel):
    d: int = 1
    tags: Optional[str] = None
    page: Optional[int] = None
    q : Optional[str] = None

class ItemTag(BaseModel):
    name: str
    category: str = "general"

class ItemPostInfo(BaseModel):
    id: int
    post_url: str = None
    file_url: str
    download_url: str
    size : str
    file_type: str
    resolution : str
    score: int
    artist_tags: List[str]
    copyrights_tags: List[str]
    characters_tags: List[str]
    general_tags: List[str]
    meta_tags:  List[str]

    # @field_validator('tags')
    # def remove_underscores(cls,v:List[str]):
    #     return [tag.replace('_',' ')  for tag in v]
    def mergeTags(self):
        return list(chain(self.artist_tags,self.copyrights_tags,self.characters_tags,self.general_tags,self.meta_tags))

    @model_validator(mode='after')
    def set_post_url(self):
        if self.post_url is None:
            self.post_url = f"https://danbooru.donmai.us/posts/{self.id}"

        return self

    def save_to_json(self,filename:str):
        with open(filename,'w',encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))

class ItemPostList(BaseModel):
    posts: List[ItemPostInfo]
    start_url : str
    start_page : int
    page_count : int

    # def save_to_json(self,filename:str):
    #     with open(filename,'w',encoding='utf-8') as f:
    #         f.write(self.model_dump_json(indent=2))

    def save_to_json(self,filename:str):
        f = Path(filename)
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(self.model_dump_json(indent=2))

