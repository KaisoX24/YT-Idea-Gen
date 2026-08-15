from core.extract_channel_info import api_key
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.data_models import VideoStats
from typing import List
from core.extract_channel_info import ChannelFetchError

def chunk_list(vid_list:list,size:int=50):
    return [vid_list[i:i+size] for i in range(0,len(vid_list),size)]

def extract_vid_stats(vid_ids:List=[])->List[VideoStats]|ChannelFetchError:
    "Extracts and returns Playlists from the channel"
    vid_stats:List[VideoStats]=[]
    chunks=chunk_list(vid_ids)
    try:
        with build('youtube','v3',developerKey=api_key) as service:
            for i in chunks:
                vid_IDs=','.join(i)
                request=service.videos().list(
                    part='statistics,contentDetails',
                    id=vid_IDs,
                    maxResults=50,
                )
                response=request.execute()

                for item in response.get("items",[]):
                    vid_stats.append(VideoStats(
                        video_id=item['id'],
                        view_count= item['statistics']['viewCount'],
                        like_count= item['statistics'].get('likeCount', 0),
                        duration= item['contentDetails']['duration'],
                    ))

        return vid_stats
    
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
