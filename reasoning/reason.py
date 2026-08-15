from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage,SystemMessage
from googleapiclient.errors import HttpError
from models.data_models import VideoIdeaList,VideoAnalytics,ChannelFetchError
from dotenv import load_dotenv
from pathlib import Path
import re
from datetime import timedelta
load_dotenv()

PROJECT_ROOT=Path(__file__).resolve().parent.parent
SYS_MSG_DIR=PROJECT_ROOT/'reasoning'/'sys_prompt'

sys_msg=None
structured_llm=None

def parse_iso_duration(duration: str) -> timedelta:
    hours_match = re.search(r'(\d+)H', duration)
    minutes_match = re.search(r'(\d+)M', duration)
    seconds_match = re.search(r'(\d+)S', duration)

    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def format_video_data(videos: list[VideoAnalytics]) -> str:
    lines = []
    for v in videos:
        video_duration=parse_iso_duration(v.duration)
        lines.append(
            f"- \"{v.title}\" — {v.view_count} views ({v.views_per_day:.1f}/day), "
            f"{v.like_count} likes, published {v.days_since} days ago, duration {video_duration}"
        )
    return "\n".join(lines)

def get_sys_msg() -> str:
    global sys_msg
    if sys_msg is None:
        sys_msg=(SYS_MSG_DIR/'sys_msg.txt').read_text(encoding='utf-8')
    return sys_msg

def init_structured_llm():
    global structured_llm
    if structured_llm is None:
        llm = init_chat_model(model="google_genai:gemini-3.5-flash",temperature=0.66)
        structured_llm=llm.with_structured_output(VideoIdeaList)
    return structured_llm

def get_ideas(
        channel_title:str,
        channel_description:str,
        sub_count:int,
        scope_label:str,
        ranked_videos:list[VideoAnalytics],
        top_n:int=15):

    top_vids=ranked_videos[:top_n]
    vid_data_blocks=format_video_data(top_vids)

    human_content=(
        f"Channel: {channel_title}",
        f"Description: {channel_description}",
        f"Subscribers: {sub_count}",
        f"Data Scope: {scope_label}",
        f"Top Performing Videos: {vid_data_blocks}"
    )

    messages=[
        SystemMessage(content=get_sys_msg()),
        HumanMessage(content=human_content)
    ]

    try:
        llm=init_structured_llm()
        result=llm.invoke(messages)
        return result
    except HttpError as e:
            status=e.resp.status
            try:
                reason=e.error_details[0].get('reason','') if e.error_details else ''
            except (AttributeError,IndexError,KeyError):
                reason=''
    
            if status==429 or (status==403 and reason in ('quotaExceeded', 'rateLimitExceeded', 'userRateLimitExceeded')):
                return ChannelFetchError.RATE_LIMITED
            
            elif status==403:
                return ChannelFetchError.FORBIDDEN
            
            return ChannelFetchError.UNKNOWN
        
    except (KeyError,IndexError):
        return ChannelFetchError.NOT_FOUND
    
