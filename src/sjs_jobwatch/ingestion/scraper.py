"""
Web scraping module for the SJS job board.

This module handles fetching and parsing job listings from the SJS website.
Uses simple HTTP requests + BeautifulSoup instead of heavyweight browser automation.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sjs_jobwatch.core import config
from sjs_jobwatch.core.models import Job, Snapshot

logger = logging.getLogger(__name__)


class ScrapeError(Exception):
    """Raised when scraping fails."""

    pass


class SJSScraper:
    """
    Scraper for the SJS New Zealand job board.
    
    The SJS site uses server-side rendering with Next.js, which means
    job data is embedded in a <script id="__NEXT_DATA__"> tag as JSON.
    This allows us to use simple HTTP requests instead of browser automation.
    """

    def __init__(
        self,
        timeout: int = config.REQUEST_TIMEOUT,
        delay: float = config.REQUEST_DELAY,
    ) -> None:
        """
        Initialize the scraper.
        
        Args:
            timeout: HTTP request timeout in seconds
            delay: Delay between requests in seconds
        """
        self.timeout = timeout
        self.delay = delay
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic and proper headers."""
        session = requests.Session()

        # Add retry logic for transient failures
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers
        session.headers.update(
            {
                "User-Agent": config.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        return session

    def scrape(
        self,
        url: str | None = None,
        region: str = "All",
        category: str = "All",
        keyword: str = "",
    ) -> Snapshot:
        """
        Scrape job listings from SJS.
        
        Args:
            url: Direct URL to scrape (overrides other params)
            region: Region filter
            category: Category filter
            keyword: Keyword search
            
        Returns:
            Snapshot containing all found jobs
            
        Raises:
            ScrapeError: If scraping fails
        """
        start_time = time.time()

        # Build URL
        target_url = url or config.get_sjs_url(region, category, keyword)
        logger.info(f"Scraping SJS jobs from: {target_url}")

        try:
            # Fetch the page
            response = self.session.get(target_url, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract job data from Next.js data script
            jobs = self._extract_jobs(soup)

            duration = time.time() - start_time
            logger.info(f"Successfully scraped {len(jobs)} jobs in {duration:.2f}s")

            # Be respectful - add delay
            time.sleep(self.delay)

            return Snapshot(
                timestamp=datetime.now(),
                jobs=jobs,
                total_count=len(jobs),
                scrape_duration_seconds=duration,
                source_url=target_url,
            )

        except requests.RequestException as e:
            raise ScrapeError(f"Failed to fetch page: {e}") from e
        except Exception as e:
            raise ScrapeError(f"Failed to parse page: {e}") from e

    def _extract_jobs(self, soup: BeautifulSoup) -> list[Job]:
        """
        Extract job listings from the parsed HTML.
        
        Looks for the __NEXT_DATA__ script tag which contains
        server-rendered job data as JSON.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            List of Job objects
            
        Raises:
            ScrapeError: If data cannot be extracted
        """
        # Find the Next.js data script
        script = soup.find("script", {"id": "__NEXT_DATA__"})

        if not script or not script.string:
            raise ScrapeError("Could not find __NEXT_DATA__ script tag")

        try:
            # Parse the JSON data
            data = json.loads(script.string)

            # Navigate to the job results (path may vary - adjust as needed)
            # This is a guess based on common Next.js patterns
            page_props = data.get("props", {}).get("pageProps", {})

            # Try multiple possible paths
            raw_jobs = None
            for path in [
                ["searchResults", "results"],
                ["jobs", "results"],
                ["results"],
                ["jobs"],
            ]:
                current = page_props
                try:
                    for key in path:
                        current = current[key]
                    if isinstance(current, list):
                        raw_jobs = current
                        break
                except (KeyError, TypeError):
                    continue

            if raw_jobs is None:
                logger.warning("Could not find job results in expected location")
                logger.debug(f"Available keys: {list(page_props.keys())}")
                # Return empty list rather than crashing
                return []

            # Convert raw job data to Job objects
            jobs = []
            for raw_job in raw_jobs:
                try:
                    job = self._parse_job(raw_job)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"Failed to parse job: {e}")
                    continue

            return jobs

        except json.JSONDecodeError as e:
            raise ScrapeError(f"Failed to decode JSON data: {e}") from e

    def _parse_job(self, raw: dict[str, Any]) -> Job | None:
        """
        Parse a single raw job dictionary into a Job object.
        
        Args:
            raw: Raw job data from JSON
            
        Returns:
            Job object or None if required fields are missing
        """
        # Extract required fields
        job_id = raw.get("jobId") or raw.get("id")
        title = raw.get("title")
        employer = raw.get("businessName") or raw.get("employer")

        # Validate required fields
        if not job_id or not title or not employer:
            logger.debug(f"Skipping job with missing required fields: {raw.get('title', 'unknown')}")
            return None

        # Build URL to the job posting
        job_url = f"https://www.sjs.govt.nz/jobs/{job_id}" if job_id else None

        # Create the Job object
        try:
            return Job(
                id=str(job_id),
                title=str(title).strip(),
                employer=str(employer).strip(),
                category=raw.get("category"),
                classification=raw.get("classification"),
                sub_classification=raw.get("subClassification"),
                job_type=raw.get("jobType") or raw.get("type"),
                region=raw.get("regionName") or raw.get("region"),
                area=raw.get("areaName") or raw.get("area"),
                summary=raw.get("summary"),
                description=raw.get("description"),
                pay_min=_parse_pay(raw.get("payMin") or raw.get("salaryMin")),
                pay_max=_parse_pay(raw.get("payMax") or raw.get("salaryMax")),
                posted_date=_parse_date(raw.get("postedDate")),
                start_date=_parse_date(raw.get("startDate")),
                end_date=_parse_date(raw.get("endDate") or raw.get("closingDate")),
                url=job_url,
            )
        except Exception as e:
            logger.warning(f"Failed to create Job object: {e}")
            return None


# Helper functions for parsing (module level for efficiency)
def _parse_date(date_str: str | None) -> datetime | None:
    """Parse ISO date string safely."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _parse_pay(value: Any) -> float | None:
    """Parse pay value safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# Convenience function for one-off scrapes
def scrape_sjs_jobs(
    url: str | None = None,
    region: str = "All",
    category: str = "All",
    keyword: str = "",
) -> Snapshot:
    """
    Convenience function to scrape SJS jobs.
    
    Args:
        url: Direct URL (overrides other params)
        region: Region filter
        category: Category filter
        keyword: Keyword search
        
    Returns:
        Snapshot of current jobs
    """
    scraper = SJSScraper()
    return scraper.scrape(url=url, region=region, category=category, keyword=keyword)
