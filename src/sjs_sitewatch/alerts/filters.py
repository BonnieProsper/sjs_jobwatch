from typing import Iterable, List

from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity


# -------------------------
# Job-level filters
# -------------------------

ICT_CATEGORIES = {"ict", "it", "information technology"}


def is_ict_job(job: Job) -> bool:
    return (job.category or "").lower() in ICT_CATEGORIES


def filter_ict(jobs: Iterable[Job]) -> List[Job]:
    return [job for job in jobs if is_ict_job(job)]


def filter_region(jobs: Iterable[Job], region: str) -> List[Job]:
    region_normalized = region.strip().lower()
    return [
        job
        for job in jobs
        if job.region and job.region.lower() == region_normalized
    ]


# -------------------------
# Alert-level filters
# -------------------------

def filter_by_min_severity(
    changes: Iterable[ScoredChange],
    min_severity: Severity,
) -> List[ScoredChange]:
    return [
        change
        for change in changes
        if change.severity > min_severity
    ]
