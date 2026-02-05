from pydantic import BaseModel
from datetime import date
from typing import List



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
    url : str = ''
    plot : str = ''
    actresses : List[EasyMode] = []
    actors : List[EasyMode] = []
    genres : List[EasyMode] = []
    series : List[EasyMode] = []
    makers : List[EasyMode] = []
    directors : List[EasyMode] = []
    tags : List[EasyMode] = []

