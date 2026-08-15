from core.extract_channel_info import api_key
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.data_models import PlaylistItem
from typing import List
from core.extract_channel_info import ChannelFetchError

def extract_playlists_items(playlist_id:str="")->List[PlaylistItem]|ChannelFetchError:
    "Extracts and returns Videos from the playlist"
    playlists_items:List[PlaylistItem]=[]
    next_page_token=None
    max_pages=20
    try:
        with build('youtube','v3',developerKey=api_key) as service:
            for _ in range(max_pages):
                request=service.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response=request.execute()

                for item in response.get("items",[]):
                    playlists_items.append(PlaylistItem(
                        vid_id=item['contentDetails']['videoId'],
                        title=item['snippet']['title'],
                        published_at=item['contentDetails']['videoPublishedAt'],
                        thumbnail_url=item['snippet']['thumbnails']['high']['url']
                    ))

                next_page_token=response.get('nextPageToken')
                if not next_page_token: break

        return playlists_items
    
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