from bs4 import BeautifulSoup

def extract_content(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No Title"
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    links = [a["href"] for a in soup.find_all("a", href=True)]
    return {
        "title": title,
        "headings": headings[:10],
        "paragraphs": paragraphs[:10],
        "links": links[:10]
    }
