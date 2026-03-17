import traceback
import streamlit as st
from urllib.parse import urlparse
from scraping_pipeline import execute_scraping

st.set_page_config(page_title="Core Scraping Module Demo using Playwright")

st.title("Core Scraping Module Testing Interface")

url_input = st.text_input("Enter Website URL")

if st.button("Start Scraping"):
    url = url_input.strip()
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            st.warning("Please enter a valid HTTP or HTTPS URL.")
        else:
            with st.spinner("Scraping in progress..."):
                try:
                    data = execute_scraping(url)
                    st.success("Scraping Completed")
                    st.subheader("Title")
                    st.write(data["title"])
                    st.subheader("Headings")
                    st.write(data["headings"])
                    st.subheader("Paragraphs")
                    st.write(data["paragraphs"])
                    st.subheader("Links")
                    st.write(data["links"])

                except Exception as e:
                    st.error(f"Error: {e!r}")
                    st.code(traceback.format_exc())