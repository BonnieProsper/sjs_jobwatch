"""
Diff engine for comparing job snapshots.

Provides deterministic, explainable diffing between two snapshots.
"""

import logging
from typing import Any

from sjs_jobwatch.core.models import DiffResult, FieldChange, Job, JobChange, Snapshot

logger = logging.getLogger(__name__)

# Fields to track for changes
TRACKED_FIELDS = [
    "title",
    "employer",
    "category",
    "classification",
    "sub_classification",
    "job_type",
    "region",
    "area",
    "summary",
    "description",
    "pay_min",
    "pay_max",
    "posted_date",
    "start_date",
    "end_date",
]


def diff_snapshots(previous: Snapshot, current: Snapshot) -> DiffResult:
    """
    Calculate differences between two snapshots.
    
    Identifies:
    - Added jobs (in current but not in previous)
    - Removed jobs (in previous but not in current)
    - Modified jobs (in both, but with changed fields)
    
    Args:
        previous: Earlier snapshot
        current: Later snapshot
        
    Returns:
        Complete diff result
    """
    logger.debug(
        f"Diffing snapshots: {previous.total_count} jobs → {current.total_count} jobs"
    )

    # Build lookup dictionaries for fast access
    previous_jobs = {job.id: job for job in previous.jobs}
    current_jobs = {job.id: job for job in current.jobs}

    added: list[JobChange] = []
    removed: list[JobChange] = []
    modified: list[JobChange] = []

    # Find added and modified jobs
    for job_id, current_job in current_jobs.items():
        if job_id not in previous_jobs:
            # New job
            added.append(
                JobChange(
                    job_id=job_id,
                    before=None,
                    after=current_job,
                    changes=[],
                )
            )
        else:
            # Potentially modified job
            previous_job = previous_jobs[job_id]
            changes = compare_jobs(previous_job, current_job)

            if changes:
                modified.append(
                    JobChange(
                        job_id=job_id,
                        before=previous_job,
                        after=current_job,
                        changes=changes,
                    )
                )

    # Find removed jobs
    for job_id, previous_job in previous_jobs.items():
        if job_id not in current_jobs:
            removed.append(
                JobChange(
                    job_id=job_id,
                    before=previous_job,
                    after=None,
                    changes=[],
                )
            )

    logger.info(
        f"Diff complete: {len(added)} added, {len(removed)} removed, {len(modified)} modified"
    )

    return DiffResult(
        previous_snapshot=previous,
        current_snapshot=current,
        added=added,
        removed=removed,
        modified=modified,
    )


def compare_jobs(old_job: Job, new_job: Job) -> list[FieldChange]:
    """
    Compare two versions of the same job and identify field changes.
    
    Args:
        old_job: Previous version
        new_job: Current version
        
    Returns:
        List of field changes
    """
    changes: list[FieldChange] = []

    for field in TRACKED_FIELDS:
        old_value = getattr(old_job, field, None)
        new_value = getattr(new_job, field, None)

        # Compare values (handle different types)
        if not _values_equal(old_value, new_value):
            changes.append(
                FieldChange(
                    field=field,
                    old_value=_serialize_value(old_value),
                    new_value=_serialize_value(new_value),
                )
            )

    return changes


def _values_equal(value1: Any, value2: Any) -> bool:
    """
    Check if two values are equal, handling special cases.
    
    Treats None, empty string, and whitespace-only strings as equivalent.
    """
    # Normalize empty/whitespace strings to None
    if isinstance(value1, str):
        value1 = value1.strip() or None
    if isinstance(value2, str):
        value2 = value2.strip() or None

    return value1 == value2


def _serialize_value(value: Any) -> str | None:
    """
    Serialize a value for display in FieldChange.
    
    Converts various types to strings in a human-readable way.
    """
    if value is None:
        return None

    if isinstance(value, (str, int, float)):
        return str(value)

    if hasattr(value, "isoformat"):  # datetime
        return value.isoformat()

    return str(value)


def summarize_diff(diff: DiffResult) -> str:
    """
    Create a human-readable summary of a diff.
    
    Args:
        diff: Diff result to summarize
        
    Returns:
        Summary string
    """
    lines = [
        f"Job changes from {diff.previous_snapshot.timestamp} to {diff.current_snapshot.timestamp}:",
        f"  {len(diff.added)} new jobs",
        f"  {len(diff.removed)} removed jobs",
        f"  {len(diff.modified)} modified jobs",
        f"  {diff.total_changes} total changes",
    ]

    return "\n".join(lines)
