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

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        return cls(value.lower())



class SeverityCalculator:
    """
    Assigns severity and explanation to a JobChange using:
    - local diff information
    - multi-day trend context

    Rules are intentionally conservative and explainable.
    """

    # -------------------------------------------------
    # Backward-compatible public API
    # -------------------------------------------------

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> Severity:
        """
        Legacy API: return severity only.
        """
        severity, _ = self._score_with_reason(
            change=change,
            trends=trends,
        )
        return severity

    def score_with_reason(
        self,
        *,
        change: JobChange,
        trends: TrendReport,
    ) -> tuple[Severity, str]:
        """
        Preferred API: return severity + explanation.
        """
        return self._score_with_reason(
            change=change,
            trends=trends,
        )

    # -------------------------------------------------
    # Internal implementation
    # -------------------------------------------------

    def _score_with_reason(
        self,
        *,
        change: JobChange,
        trends: TrendReport,
    ) -> tuple[Severity, str]:
        job_id = change.job_id

        salary_changed_ids = {sc.job_id for sc in trends.salary_changes}
        title_changed_ids = {tc.job_id for tc in trends.title_changes}

        # Job added → HIGH
        if change.before is None and change.after is not None:
            return Severity.HIGH, "New job posting detected"

        # Job removed → MEDIUM
        if change.before is not None and change.after is None:
            return Severity.MEDIUM, "Job posting was removed"

        # Modified job
        if change.before is not None and change.after is not None:
            if job_id in salary_changed_ids:
                return Severity.HIGH, "Salary changed on an existing job"

            if job_id in title_changed_ids:
                if job_id in trends.persistent_jobs:
                    return Severity.HIGH, "Title changed on a long-running job"
                return Severity.MEDIUM, "Title changed on a recent job"

            if job_id in trends.persistent_jobs:
                return Severity.MEDIUM, "Update detected on a long-running job"

        return Severity.LOW, "Minor or routine update"
