from typing import Iterable

from sjs_sitewatch.ingestion.normalize import Job


def filter_by_region(
    jobs: Iterable[Job],
    region: str,
) -> list[Job]:
    region = region.lower()
    return [
        job for job in jobs
        if job.region and job.region.lower() == region
    ]
