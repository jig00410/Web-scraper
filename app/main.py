import streamlit as st

def main():
    st.set_page_config(page_title="Web Scrape - Automated Data Extraction Tool", layout="wide")
    st.title("Web Scrape - Automated Data Extraction Tool")
    st.write("Enter a URL to start scraping data from the web. This tool allows you to extract information from websites and save it in a structured format.")

if __name__ == "__main__":
    main()
