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

def extract_content_by_tags(soup, selected_tags):
    extracted_data = []

    for tag_info in selected_tags:
        tag_name = tag_info.get("tag")
        attrs = tag_info.get("attrs", {})

        elements = soup.find_all(tag_name, attrs=attrs)

        for el in elements:
            text = el.get_text(strip=True)
            if text:
                extracted_data.append({
                    "tag": tag_name,
                    "attrs": attrs,
                    "text": text
                })

    return extracted_data