import sys
import asyncio
from playwright.sync_api import sync_playwright

def _configure_windows_event_loop_policy():
    if sys.platform != "win32":
        return
    current_policy = asyncio.get_event_loop_policy()
    if not isinstance(current_policy, asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def launch_browser():
    _configure_windows_event_loop_policy()
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    return playwright, browser

def close_browser(playwright, browser):
    browser.close()
    playwright.stop()
