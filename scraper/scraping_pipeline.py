from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_processor import process_html
from scraper.tag_tree_builder import build_tag_tree
from scraper.content_extractor import extract_content_by_tags
from scraper.tag_tree_optimizer import optimize_tag_tree
from scraper.url_validator import validate_url

# LLM functions (import from llm/)
from llm.tag_selector import select_relevant_tags
from llm.data_processor import process_extracted_data


def execute_scraping(url, query):
    if not validate_url(url):
        raise ValueError("Invalid or unreachable URL")

    playwright, browser = launch_browser()

    try:
        # Step 1: Load page
        raw_html = load_page(browser, url)

        # Step 2: Clean HTML
        soup = process_html(raw_html)

        # Step 3: Build tag tree
        tag_tree = build_tag_tree(soup)

        # Step 4: Send to LLM → get relevant tags
        selected_tags = select_relevant_tags(query, tag_tree)

        # Step 5: Extract content using filtered tags
        extracted_data = extract_content_by_tags(soup, selected_tags)

        # Step 6: Send back to LLM for formatting
        final_output = process_extracted_data(query, extracted_data)

        return final_output

    finally:
        close_browser(playwright, browser)