import asyncio
import sys


def _fix_windows_asyncio():
    """
    Critical fix for Windows Python 3.13/3.14.
    The default ProactorEventLoop on Windows does NOT work with Playwright sync API.
    Must be called at module level before any Playwright import.
    """
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except AttributeError:
            try:
                loop = asyncio.SelectorEventLoop()
                asyncio.set_event_loop(loop)
            except Exception:
                pass


# Apply fix immediately at import time
_fix_windows_asyncio()


def _err(msg: str) -> dict:
    return {"success": False, "title": "", "headings": [], "error": msg}


def scrape_website_data(url: str) -> dict:
    """
    Scrape a URL using Playwright headless Chromium.
    Returns: {"success": bool, "title": str, "headings": list[str], "error": str}
    """
    # Validate
    if not url or not isinstance(url, str):
        return _err("No URL provided.")
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return _err("URL must start with http:// or https://")

    # Import check
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return _err("Playwright not installed. Run: pip install playwright && playwright install chromium")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
            )
            page = ctx.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            except PWTimeout:
                browser.close()
                return _err("Page timed out (60s). Site may be slow or blocking bots.")
            except Exception as e:
                browser.close()
                return _err(f"Navigation failed: {e}")

            try:
                page.wait_for_timeout(1500)
            except Exception:
                pass

            page_title = page.title() or url

            selector_groups = [
                "h1", "h2", "h3",
                ".titleline > a",
                ".story-title a",
                "article h2", "article h3",
                ".post-title", ".entry-title", ".article-title",
                ".product-title", "[class*='title']",
                "h4", "h5",
                "a[class*='title']",
                "p",
            ]

            seen = set()
            data = []

            for sel in selector_groups:
                try:
                    els = page.query_selector_all(sel)
                    for el in els:
                        try:
                            txt = el.inner_text().strip()
                        except Exception:
                            continue
                        if txt and txt not in seen and 3 < len(txt) < 500:
                            seen.add(txt)
                            data.append(txt)
                except Exception:
                    continue
                if len(data) >= 50:
                    break

            browser.close()

            if not data:
                return _err("No text content found. The page may require login or block scrapers.")

            return {"success": True, "title": page_title, "headings": data[:50], "error": ""}

    except Exception as e:
        return _err(str(e))
