from typing import List, Dict, Any
from playwright.async_api import async_playwright


async def capture_jobs() -> List[Dict[str, Any]]:
    """
    Launches a real browser, listens for SJS job API responses,
    and returns all captured job records as raw dicts.
    """
    jobs: list[dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def handle_response(response):
            if "/prod/jobs" not in response.url:
                return

            try:
                payload = await response.json()
            except Exception:
                return

            # SJS returns a raw list of jobs
            if isinstance(payload, list):
                jobs.extend(payload)

            # Defensive: some APIs wrap data
            elif isinstance(payload, dict):
                records = payload.get("jobs") or payload.get("data") or []
                if isinstance(records, list):
                    jobs.extend(records)

        page.on("response", handle_response)

        await page.goto("https://www.sjs.co.nz", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        await browser.close()

    return jobs
