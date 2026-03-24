from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

'''import requests

def validate_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except Exception:
        return False'''