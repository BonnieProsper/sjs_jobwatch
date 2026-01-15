from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Set

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

    @classmethod
    def empty(cls) -> "TrendReport":
        return cls(
            job_counts_by_day={},
            persistent_jobs=[],
            new_jobs=[],
            removed_jobs=[],
            title_changes=[],
            salary_changes=[],
        )


# -------------------------
# Analyzer
# -------------------------

class TrendAnalyzer:
    """
    Analyze multiple snapshots over time and extract multi-day trends.

    Rules:
    - disappearance followed by reappearance counts as removed + new
    - persistence requires presence on *every* day
    """

    def __init__(self, snapshots: Iterable[Snapshot]) -> None:
        self._snapshots = sorted(snapshots, key=lambda s: s.captured_at)

    def analyze(self) -> TrendReport:
        if not self._snapshots:
            return TrendReport.empty()

        job_counts: Dict[date, int] = {}
        jobs_by_day: Dict[date, Set[str]] = {}

        title_changes: List[TitleChange] = []
        salary_changes: List[SalaryChange] = []

        previous_jobs: Dict[str, Job] = {}

        for snapshot in self._snapshots:
            day = snapshot.captured_at.date()
            current_jobs = snapshot.jobs

            job_counts[day] = len(current_jobs)
            jobs_by_day[day] = set(current_jobs.keys())

            for job_id, job in current_jobs.items():
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

            previous_jobs = dict(current_jobs)

        all_days = sorted(jobs_by_day.keys())
        first_day = all_days[0]
        last_day = all_days[-1]

        all_job_ids = set().union(*jobs_by_day.values())

        persistent_jobs: List[str] = []
        new_jobs: List[str] = []
        removed_jobs: List[str] = []

        for job_id in all_job_ids:
            present_days = [d for d in all_days if job_id in jobs_by_day[d]]

            if len(present_days) == len(all_days):
                persistent_jobs.append(job_id)

            if job_id in jobs_by_day[last_day] and job_id not in jobs_by_day[first_day]:
                new_jobs.append(job_id)

            if job_id not in jobs_by_day[last_day] and job_id in jobs_by_day[first_day]:
                removed_jobs.append(job_id)

            # gap detection → removed + new
            if len(present_days) >= 2:
                for d1, d2 in zip(present_days, present_days[1:]):
                    if (d2 - d1).days > 1:
                        if job_id not in new_jobs:
                            new_jobs.append(job_id)
                        if job_id not in removed_jobs:
                            removed_jobs.append(job_id)
                        if job_id in persistent_jobs:
                            persistent_jobs.remove(job_id)
                        break

        return TrendReport(
            job_counts_by_day=job_counts,
            persistent_jobs=sorted(persistent_jobs),
            new_jobs=sorted(set(new_jobs)),
            removed_jobs=sorted(set(removed_jobs)),
            title_changes=title_changes,
            salary_changes=salary_changes,
        )
