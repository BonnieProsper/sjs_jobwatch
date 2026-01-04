from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import async_playwright, Page


@asynccontextmanager
async def launch_browser(headless: bool = True) -> AsyncIterator[Page]:
    """
    Context-managed browser lifecycle.

    Intentionally thin:
    - No site logic
    - No interception
    - No retries

    Keeps Playwright usage isolated and replaceable.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            yield page
        finally:
            await context.close()
            await browser.close()
