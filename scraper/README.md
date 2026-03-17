# Scraper Layer

This folder contains all web scraping related logic.

It handles:
- Opening websites using Playwright
- Loading page content
- Extracting HTML data
- Cleaning unnecessary tags
- Selecting required information

This layer collects raw data from websites.

## Run the Demo App
Use these steps to test the scraper module using the demo interface:

1. Open a terminal in the `scraper/` folder.

2. Run:

```powershell
streamlit run .\demo_app.py
```

3. In the Streamlit page:
	- Enter a website URL.
	- Click **Start Scraping**.
	- View extracted title, headings, paragraphs, and links.