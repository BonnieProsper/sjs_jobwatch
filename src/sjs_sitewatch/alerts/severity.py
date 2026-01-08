from enum import IntEnum

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.trends import TrendReport

__all__ = [
    "Severity",
    "SeverityCalculator",
]


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SeverityCalculator:
    """
    Assigns severity and explanation to a JobChange using:
    - local diff information
    - multi-day trend context

    Rules are intentionally conservative and explainable.
    """

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> tuple[Severity, str]:
        job_id = change.job_id

        # -------------------------------------------------
        # Job added → always HIGH
        # -------------------------------------------------
        if change.before is None and change.after is not None:
            return (
                Severity.HIGH,
                "New job posting detected",
            )

        # -------------------------------------------------
        # Job removed → MEDIUM
        # -------------------------------------------------
        if change.before is not None and change.after is None:
            return (
                Severity.MEDIUM,
                "Job posting was removed",
            )

        # -------------------------------------------------
        # Modified job → trend-aware scoring
        # -------------------------------------------------
        if change.before is not None and change.after is not None:
            if any(sc.job_id == job_id for sc in trends.salary_changes):
                return (
                    Severity.HIGH,
                    "Salary changed on an existing job",
                )

            if any(tc.job_id == job_id for tc in trends.title_changes):
                if job_id in trends.persistent_jobs:
                    return (
                        Severity.HIGH,
                        "Title changed on a long-running job",
                    )
                return (
                    Severity.MEDIUM,
                    "Title changed on a recent job",
                )

            if job_id in trends.persistent_jobs:
                return (
                    Severity.MEDIUM,
                    "Update detected on a long-running job",
                )

        # -------------------------------------------------
        # Everything else
        # -------------------------------------------------
        return (
            Severity.LOW,
            "Minor or routine update",
        )
