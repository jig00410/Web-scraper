from bs4 import BeautifulSoup

def process_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unnecessary tags
    for tag in soup(["link","script", "style", "noscript"]):
        tag.decompose()

    return soup