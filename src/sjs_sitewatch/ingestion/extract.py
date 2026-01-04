from __future__ import annotations

import json
from typing import Any, List, Dict

from playwright.async_api import Page


SJS_JOB_DATA_SELECTOR = "script#__NEXT_DATA__"


async def extract_raw_jobs(page: Page) -> List[Dict[str, Any]]:
    """
    Extract raw job payloads from the SJS job listings page.

    This layer:
    - Knows about SJS HTML / JS structure
    - Returns raw dictionaries
    - Does NOT normalize or validate
    """

    script = await page.query_selector(SJS_JOB_DATA_SELECTOR)
    if script is None:
        raise RuntimeError("Unable to locate SJS job data script")

    raw_json = await script.inner_text()
    data = json.loads(raw_json)

    # This path is site-specific by design
    try:
        jobs = (
            data["props"]["pageProps"]["searchResults"]["results"]
        )
    except KeyError as exc:
        raise RuntimeError("Unexpected SJS data structure") from exc

    if not isinstance(jobs, list):
        raise RuntimeError("SJS job results is not a list")

    return jobs
