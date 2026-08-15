from pydantic import BaseModel,Field
from enum import Enum,auto
from typing import List

class ChanneInfo(BaseModel):
    channel_id:str
    uploads_id:str
    title:str
    description:str
    sub_count:int
    avatar_url:str|None

class PlaylistInfo(BaseModel):
    id: str
    title: str
    item_count: int
    description: str

class PlaylistItem(BaseModel):
    vid_id:str
    title:str
    published_at:str
    thumbnail_url:str

class VideoStats(BaseModel):
    video_id: str
    view_count: int
    like_count: int
    duration: str

class VideoAnalytics(BaseModel):
    video_id:str
    title:str
    published_at:str
    view_count:int
    like_count:int
    duration:str
    days_since:int
    views_per_day:float
    views_per_sub:float

class ImpactLevel(str,Enum):
    HIGH='HIGH'
    MEDIUM='MEDIUM'
    LOW='LOW'

class VideoIdea(BaseModel):
    title:str=Field(description='A catchy, specific video title')
    concept:str=Field(description='1-2 sentence explanation of the video idea')
    reasoning:str=Field(description='Why this idea fits the channel, referencing specific data')
    impact:ImpactLevel=Field(description='Predicted performance impact: High, Medium, or Low')

class VideoIdeaList(BaseModel):
    ideas:List[VideoIdea]
    
class ChannelFetchError(Enum):
    NOT_FOUND = auto()
    RATE_LIMITED = auto()
    FORBIDDEN = auto()
    UNKNOWN = auto()