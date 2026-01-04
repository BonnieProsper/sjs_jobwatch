from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .job import Job


@dataclass(frozen=True)
class FieldChange:
    field: str
    before: Any
    after: Any


@dataclass(frozen=True)
class JobChange:
    job_id: str
    before: Optional[Job]
    after: Optional[Job]
    changes: List[FieldChange]


@dataclass(frozen=True)
class DiffResult:
    added: List[JobChange]
    removed: List[JobChange]
    modified: List[JobChange]


TRACKED_FIELDS = (
    "title",
    "employer",
    "summary",
    "description",
    "category",
    "classification",
    "sub_classification",
    "job_type",
    "region",
    "area",
    "pay_min",
    "pay_max",
)


def compare_jobs(old: Job, new: Job) -> List[FieldChange]:
    changes: List[FieldChange] = []

    for field in TRACKED_FIELDS:
        before = getattr(old, field)
        after = getattr(new, field)

        if before != after:
            changes.append(FieldChange(field, before, after))

    return changes


def diff_snapshots(
    previous: Dict[str, Job],
    current: Dict[str, Job],
) -> DiffResult:
    added: List[JobChange] = []
    removed: List[JobChange] = []
    modified: List[JobChange] = []

    for job_id, job in current.items():
        if job_id not in previous:
            added.append(JobChange(job_id, None, job, []))
            continue

        old = previous[job_id]
        changes = compare_jobs(old, job)

        if changes:
            modified.append(
                JobChange(
                    job_id=job_id,
                    before=old,
                    after=job,
                    changes=changes,
                )
            )

    for job_id, job in previous.items():
        if job_id not in current:
            removed.append(JobChange(job_id, job, None, []))

    return DiffResult(
        added=added,
        removed=removed,
        modified=modified,
    )
