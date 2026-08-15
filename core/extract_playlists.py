from core.extract_channel_info import api_key
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.data_models import PlaylistInfo
from typing import List
from core.extract_channel_info import ChannelFetchError

def extract_playlists(channel_id:str="")->List[PlaylistInfo]|ChannelFetchError:
    "Extracts and returns Playlists from the channel"
    playlists:List[PlaylistInfo]=[]
    next_page_token=None
    max_pages=20
    try:
        with build('youtube','v3',developerKey=api_key) as service:
            for _ in range(max_pages):
                request=service.playlists().list(
                    part='snippet,contentDetails',
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response=request.execute()

                for item in response.get("items",[]):
                    item_count=item['contentDetails']['itemCount']
                    if item_count==0: continue
                    playlists.append(PlaylistInfo(
                        id=item['id'],
                        title=item['snippet']['title'],
                        item_count=item_count,
                        description=item['snippet']['description']
                    ))

                next_page_token=response.get('nextPageToken')
                if not next_page_token: break

        return playlists
    
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

