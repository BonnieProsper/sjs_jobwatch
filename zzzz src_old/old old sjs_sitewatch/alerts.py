from __future__ import annotations

from typing import Dict, List, TypedDict

from sjs_sitewatch.domain.diff import JobDiff, JobChange
from sjs_sitewatch.alerts.filters import is_ict_job
from sjs_sitewatch.ingestion.normalize import Job


SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


class AlertPayload(TypedDict):
    added: List[Job]
    removed: List[Job]
    updated: Dict[str, tuple[Job, Job, List[JobChange]]]


def has_required_severity(
    changes: List[JobChange],
    min_severity: str | None,
) -> bool:
    if not min_severity:
        return True

    threshold = SEVERITY_ORDER[min_severity.upper()]
    return any(
        SEVERITY_ORDER[change.severity] >= threshold
        for change in changes
    )


def select_alerts(
    diff: JobDiff,
    *,
    ict_only: bool = False,
    region: str | None = None,
    severity: str | None = None,
) -> AlertPayload:
    added = diff.added
    removed = diff.removed
    updated = diff.updated

    if ict_only:
        added = [job for job in added if is_ict_job(job)]
        removed = [job for job in removed if is_ict_job(job)]
        updated = {
            job_id: change
            for job_id, change in updated.items()
            if is_ict_job(change[1])
        }

    if region:
        region_lc = region.lower()
        added = [
            job for job in added
            if job.region and job.region.lower() == region_lc
        ]
        removed = [
            job for job in removed
            if job.region and job.region.lower() == region_lc
        ]
        updated = {
            job_id: change
            for job_id, change in updated.items()
            if change[1].region
            and change[1].region.lower() == region_lc
        }

    updated = {
        job_id: change
        for job_id, change in updated.items()
        if has_required_severity(change[2], severity)
    }

    return {
        "added": added,
        "removed": removed,
        "updated": updated,
    }
