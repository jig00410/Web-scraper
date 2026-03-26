def extract_by_target_tags(soup, tag_list):
    extracted = []

    for tag in tag_list:
        elements = soup.find_all(tag)

        for el in elements:
            text = el.get_text(strip=True)

            if text and len(text) > 20:
                extracted.append({
                    "tag": tag,
                    "html": str(el),
                    "text": text
                })

    return extracted