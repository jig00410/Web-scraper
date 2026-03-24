import sys
import os
import json
import re
import streamlit as st

# Fix import path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Scraper modules
from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_processor import process_html
from scraper.tag_tree_builder import build_tag_tree
from scraper.tag_tree_optimizer import optimize_tag_tree
from scraper.content_extractor import extract_content_by_tags
from scraper.url_validator import validate_url
from llm.data_refiner import refine_structured_data

# LLM modules
from llm.tag_selector import select_relevant_tags
from llm.data_processor import process_extracted_data

# -------------------------
# Helper: Extract JSON safely
# -------------------------
def extract_json(text):
    match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
    return match.group(0) if match else None


# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="AI Web Scraper", layout="wide")

st.title("🔍 AI-Powered Web Scraper")
st.markdown("Enter a URL and query to extract structured data using LLM-guided scraping.")

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
    if not validate_url(url):
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
            st.code(raw_html[:5000], language="html")

        # -------------------------
        # Step 3: Process HTML
        # -------------------------
        st.subheader("3️⃣ HTML Processing")
        soup = process_html(raw_html)
        st.success("✅ HTML cleaned")

        # -------------------------
        # Step 4: Tag Tree
        # -------------------------
        st.subheader("4️⃣ Tag Tree Generation")
        tag_tree = build_tag_tree(soup)
        tag_tree = optimize_tag_tree(tag_tree)

        st.success("✅ Tag tree generated")

        with st.expander("View Tag Tree"):
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
        # Step 7: Final Processing
        # -------------------------
        st.subheader("7️⃣ Final Data Processing")

        final_output = process_extracted_data(query, extracted_data)

        st.success("✅ Final output generated")

        # 🔍 Debug (optional)
        # st.code(final_output)

        # -------------------------
        # Fix LLM JSON issues
        # -------------------------
        if isinstance(final_output, str):
            cleaned = extract_json(final_output)

            if cleaned:
                try:
                    final_output = json.loads(cleaned)
                except:
                    st.error("❌ JSON parsing failed")
                    st.write(final_output)
                    st.stop()
            else:
                st.error("❌ No JSON found in LLM output")
                st.write(final_output)
                st.stop()

        # -------------------------
        # Extract main data
        # -------------------------
        key = list(final_output.keys())[0]
        data_list = final_output.get(key, [])

        # -------------------------
        # Pandas Refinement
        # -------------------------
        df = refine_structured_data(data_list)

        # -------------------------
        # Display Table
        # -------------------------
        st.markdown("### 📊 Refined Table")
        st.dataframe(df, use_container_width=True)

        # -------------------------
        # Sort if price exists
        # -------------------------
        if 'price' in df.columns:
            df = df.sort_values(by='price', ascending=False)

        # -------------------------
        # Download CSV
        # -------------------------
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "📥 Download CSV",
            csv,
            "output.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    finally:
        close_browser(playwright, browser)