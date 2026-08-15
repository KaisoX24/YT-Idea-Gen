from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.data_models import ChanneInfo,ChannelFetchError

# API Initiation
load_dotenv()
api_key=os.getenv("YT_DATA_API")

def channel_data(handle:str) -> ChanneInfo:
    "Extracts the Channel Data"
    try:
        with build('youtube','v3',developerKey=api_key) as service:
            request=service.channels().list(
                part="id,contentDetails,statistics,snippet",
                forHandle=handle
            )
            response=request.execute()

        if not response.get("items"):
            return ChannelFetchError.NOT_FOUND

        item = response["items"][0]
        return ChanneInfo(channel_id=item['id'],
                        uploads_id=item['contentDetails']['relatedPlaylists']['uploads'],
                        title=item['snippet']['title'],
                        description=item['snippet']['description'],
                        sub_count=item['statistics']['subscriberCount'],
                        avatar_url=item['snippet']['thumbnails']['high']['url'])
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