def load_page(browser, url: str) -> str:
    page = browser.new_page()
    page.goto(url, timeout=60000)
    page.wait_for_load_state("networkidle")
    return page.content()