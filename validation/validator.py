from urllib.parse import urlparse

def validate_url(url:str) ->bool:
    "Checks if the Passed URL is Valid"
    try:
        result=urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

