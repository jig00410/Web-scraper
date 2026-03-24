import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if project_root not in sys.path:
     sys.path.insert(0, project_root)

import streamlit as st
import json

from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_processor import process_html
from scraper.tag_tree_builder import build_tag_tree
from scraper.tag_tree_optimizer import optimize_tag_tree
from scraper.content_extractor import extract_content_by_tags
from scraper.url_validator import validate_url

from llm.tag_selector import select_relevant_tags
from llm.data_processor import process_extracted_data

from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Web Scraper", layout="wide")

st.title("🔍 AI-Powered Web Scraper")
st.markdown("Enter a URL and query to extract structured data using LLM-guided scraping.")

# -------------------------
# USER INPUT
# -------------------------
url = st.text_input("🌐 Enter URL")
query = st.text_area("❓ Enter Query (What do you want to extract?)")

run_button = st.button("🚀 Run Scraper")


# -------------------------
# MAIN EXECUTION
# -------------------------
if run_button:

    if not url or not query:
        st.warning("Please enter both URL and Query")
        st.stop()

    # Step 1: Validate URL
    st.subheader("1️⃣ URL Validation")
    is_valid = validate_url(url)

    if not is_valid:
        st.error("❌ Invalid or unreachable URL")
        st.stop()
    else:
        st.success("✅ URL is valid")

    playwright, browser = launch_browser()

    try:
        # -------------------------
        # Step 2: Load Page
        # -------------------------
        st.subheader("2️⃣ Page Loading")
        raw_html = load_page(browser, url)
        st.success("✅ Page loaded successfully")

        with st.expander("View Raw HTML"):
            st.code(raw_html[:5000], language="html")  # limit for UI

        # -------------------------
        # Step 3: Process HTML
        # -------------------------
        st.subheader("3️⃣ HTML Processing")
        soup = process_html(raw_html)
        st.success("✅ HTML cleaned")

        with st.expander("View Cleaned HTML"):
            st.code(str(soup.prettify())[:5000], language="html")

        # -------------------------
        # Step 4: Tag Tree
        # -------------------------
        st.subheader("4️⃣ Tag Tree Generation")
        tag_tree = build_tag_tree(soup)

        st.success("✅ Tag tree generated")

        with st.expander("View Tag Tree (Preview)"):
            st.json(tag_tree)

        # -------------------------
        # Step 5: LLM Tag Selection
        # -------------------------
        st.subheader("5️⃣ LLM Tag Selection")

        selected_tags = select_relevant_tags(query, tag_tree)

        st.success("✅ Relevant tags identified")

        st.json(selected_tags)

        # -------------------------
        # Step 6: Content Extraction
        # -------------------------
        st.subheader("6️⃣ Content Extraction")

        extracted_data = extract_content_by_tags(soup, selected_tags)

        st.success(f"✅ Extracted {len(extracted_data)} items")

        with st.expander("View Extracted Data"):
            st.json(extracted_data)

        # -------------------------
        # Step 7: Final LLM Processing
        # -------------------------
        st.subheader("7️⃣ Final Data Processing")

        final_output = process_extracted_data(query, extracted_data)

        st.success("✅ Final output generated")

        st.markdown("### 📊 Final Output")
        st.write(final_output)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    finally:
        close_browser(playwright, browser)