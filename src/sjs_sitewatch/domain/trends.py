from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.snapshot import Snapshot


# -------------------------
# Atomic trend events
# -------------------------

@dataclass(frozen=True)
class TitleChange:
    job_id: str
    before: str
    after: str
    day: date


@dataclass(frozen=True)
class SalaryChange:
    job_id: str
    before_min: float | None
    after_min: float | None
    before_max: float | None
    after_max: float | None
    day: date


# -------------------------
# Aggregate trend report
# -------------------------

@dataclass(frozen=True)
class TrendReport:
    job_counts_by_day: Dict[date, int]

    persistent_jobs: List[str]
    new_jobs: List[str]
    removed_jobs: List[str]

    title_changes: List[TitleChange]
    salary_changes: List[SalaryChange]


# -------------------------
# Analyzer
# -------------------------

class TrendAnalyzer:
    """
    Analyze multiple snapshots over time and extract multi-day trends.

    PURE:
    - no I/O
    - no rendering
    - no alerting
    """

    def __init__(self, snapshots: Iterable[Snapshot]) -> None:
        self._snapshots = sorted(
            snapshots,
            key=lambda s: s.captured_at,
        )

    def analyze(self) -> TrendReport:
        job_counts: Dict[date, int] = {}
        appearances: Dict[str, List[date]] = defaultdict(list)

        title_changes: List[TitleChange] = []
        salary_changes: List[SalaryChange] = []

        previous_jobs: Dict[str, Job] = {}

        for snapshot in self._snapshots:
            day = snapshot.captured_at.date()
            current_jobs = snapshot.jobs

            job_counts[day] = len(current_jobs)

            for job_id, job in current_jobs.items():
                appearances[job_id].append(day)

                if job_id in previous_jobs:
                    prev = previous_jobs[job_id]

                    if job.title != prev.title:
                        title_changes.append(
                            TitleChange(
                                job_id=job_id,
                                before=prev.title,
                                after=job.title,
                                day=day,
                            )
                        )

                    if (
                        job.pay_min != prev.pay_min
                        or job.pay_max != prev.pay_max
                    ):
                        salary_changes.append(
                            SalaryChange(
                                job_id=job_id,
                                before_min=prev.pay_min,
                                after_min=job.pay_min,
                                before_max=prev.pay_max,
                                after_max=job.pay_max,
                                day=day,
                            )
                        )

            previous_jobs = current_jobs

        all_days = sorted(job_counts.keys())
        total_days = len(all_days)

        persistent_jobs = [
            job_id
            for job_id, days in appearances.items()
            if len(days) == total_days
        ]

        new_jobs = [
            job_id
            for job_id, days in appearances.items()
            if days[0] == all_days[-1]
        ]

        removed_jobs = [
            job_id
            for job_id, days in appearances.items()
            if days[-1] != all_days[-1]
        ]

        return TrendReport(
            job_counts_by_day=job_counts,
            persistent_jobs=persistent_jobs,
            new_jobs=new_jobs,
            removed_jobs=removed_jobs,
            title_changes=title_changes,
            salary_changes=salary_changes,
        )
