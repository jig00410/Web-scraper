import sys
import os
import json

# Fix import path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_cleaner import clean_html
from scraper.target_extractor import extract_by_target_tags
from scraper.compact_tree_builder import build_compact_tree
from scraper.url_validator import validate_url

from llm.tag_identifier import identify_target_tags
from llm.data_processor import process_extracted_data


# -------------------------
# HELPER: SIZE FORMATTER
# -------------------------
def format_size(data):
    size = len(data.encode("utf-8"))

    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} TB"


# -------------------------
# STREAMLIT CONFIG
# -------------------------
st.set_page_config(page_title="Query-Driven Web Scraper", layout="wide")

st.title("🧠 Query-Driven AI Web Scraper")
st.markdown("Efficient scraping using **LLM-guided tag selection + targeted extraction**")

# -------------------------
# INPUT
# -------------------------
url = st.text_input("🌐 Enter URL")
query = st.text_area("❓ Enter Query")

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

    if not validate_url(url):
        st.error("❌ Invalid URL")
        st.stop()

    st.success("✅ URL is valid")

    playwright, browser = launch_browser()

    try:
        # -------------------------
        # PARALLEL TASKS
        # -------------------------
        st.subheader("2️⃣ Parallel Execution")

        with st.spinner("Running parallel tasks..."):
            raw_html = load_page(browser, url)
            tag_list = identify_target_tags(query)

        st.success("✅ HTML Loaded & Tags Identified")

        # -------------------------
        # RAW HTML
        # -------------------------
        st.subheader("3️⃣ Raw HTML")

        st.write(f"📦 Size: {format_size(raw_html)}")

        with st.expander("View Raw HTML"):
            st.code(raw_html[:5000], language="html")

        # -------------------------
        # CLEAN HTML
        # -------------------------
        st.subheader("4️⃣ Cleaned HTML")

        soup = clean_html(raw_html)
        cleaned_html = str(soup)

        st.write(f"📦 Size: {format_size(cleaned_html)}")

        reduction = (
            (len(raw_html) - len(cleaned_html)) / len(raw_html) * 100
            if len(raw_html) > 0 else 0
        )

        st.write(f"📉 Reduction: {reduction:.2f}%")

        with st.expander("View Cleaned HTML"):
            st.code(cleaned_html[:5000], language="html")

        # -------------------------
        # LLM TAG OUTPUT
        # -------------------------
        st.subheader("5️⃣ LLM Tag Identification")

        st.json(tag_list)

        # -------------------------
        # EXTRACTION
        # -------------------------
        st.subheader("6️⃣ Targeted Extraction")

        extracted_data = extract_by_target_tags(soup, tag_list)

        st.success(f"✅ Extracted {len(extracted_data)} elements")

        with st.expander("View Extracted Data"):
            st.json(extracted_data)

        # -------------------------
        # COMPACT TREE
        # -------------------------
        st.subheader("7️⃣ Compact Tag Tree")

        compact_tree = build_compact_tree(extracted_data)

        compact_tree_str = json.dumps(compact_tree)

        st.write(f"📦 Size: {format_size(compact_tree_str)}")

        with st.expander("View Compact Tree"):
            st.json(compact_tree)

        # -------------------------
        # FINAL LLM OUTPUT
        # -------------------------
        st.subheader("8️⃣ Final LLM Processing")

        final_output = process_extracted_data(query, compact_tree)

        st.success("✅ Final Output Generated")

        st.markdown("### 📊 Result")
        st.write(final_output)

    except Exception as e:
        import traceback
        st.error(f"❌ Error: {str(e)}")
        st.code(traceback.format_exc())

    finally:
        close_browser(playwright, browser)
