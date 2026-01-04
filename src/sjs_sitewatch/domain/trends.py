from collections import Counter
from typing import Dict, Iterable, List

from .snapshot import Snapshot


def total_jobs(snapshot: Snapshot) -> int:
    return len(snapshot.jobs)


def jobs_by_region(snapshot: Snapshot) -> Dict[str, int]:
    return Counter(
        job.region
        for job in snapshot.jobs.values()
        if job.region
    )


def job_growth(previous: Snapshot, current: Snapshot) -> int:
    return len(current.jobs) - len(previous.jobs)


def region_growth(previous: Snapshot, current: Snapshot) -> Dict[str, int]:
    prev = jobs_by_region(previous)
    curr = jobs_by_region(current)

    delta: Dict[str, int] = {}
    keys = set(prev) | set(curr)

    for key in keys:
        delta[key] = curr.get(key, 0) - prev.get(key, 0)

    return delta


def rolling_job_growth(
    snapshots: List[Snapshot],
    days: int = 7,
) -> int | None:
    """
    Compute job count growth between the latest snapshot
    and the snapshot N positions earlier.

    Note: this is index-based, not time-based.
    """
    if len(snapshots) <= days:
        return None

    return len(snapshots[-1].jobs) - len(snapshots[-days - 1].jobs)


def rolling_churn(snapshots: Iterable[Snapshot]) -> int:
    total = 0
    snaps = list(snapshots)

    for prev, curr in zip(snaps, snaps[1:]):
        total += abs(len(curr.jobs) - len(prev.jobs))

    return total
