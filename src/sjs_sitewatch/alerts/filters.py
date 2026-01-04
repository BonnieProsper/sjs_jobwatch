from typing import Iterable, List

from sjs_sitewatch.domain.job import Job


ICT_KEYWORDS = {
    "software",
    "developer",
    "engineer",
    "engineering",
    "it",
    "information technology",
    "data",
    "programmer",
    "systems",
    "network",
    "cloud",
    "devops",
    "administrator",
    "admin",
}


def _safe_text(*values: str | None) -> str:
    """
    Join optional strings into a single lowercase blob for matching.
    """
    return " ".join(v for v in values if v).lower()


def is_ict_job(job: Job) -> bool:
    """
    Heuristic check for ICT-related roles based on
    title + summary keyword matching.
    """
    text = _safe_text(job.title, job.summary)
    return any(keyword in text for keyword in ICT_KEYWORDS)


def filter_ict(jobs: Iterable[Job]) -> List[Job]:
    """
    Filters a collection of jobs to ICT-only roles.
    """
    return [job for job in jobs if is_ict_job(job)]


def filter_region(jobs: Iterable[Job], region: str) -> List[Job]:
    """
    Filters jobs by case-insensitive exact region match.
    """
    region_normalized = region.strip().lower()

    return [
        job
        for job in jobs
        if job.region and job.region.lower() == region_normalized
    ]
