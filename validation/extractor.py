from validation.validator import validate_url

def yt_handle_extractor(url:str) -> str:
    "Extracts the YT Handle from the Given Channel URL"
    if validate_url(url) and '@' in url:
        return url[url.rindex('@'):].split('/')[0]
    return None