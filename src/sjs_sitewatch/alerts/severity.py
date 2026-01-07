from enum import IntEnum

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.trends import TrendReport


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SeverityCalculator:
    """
    Assigns severity to a JobChange using:
    - local diff information
    - multi-day trend context

    Rules are intentionally conservative and explainable.
    """

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> Severity:
        job_id = change.job_id

        # --- Job added ---
        if change.before is None and change.after is not None:
            return Severity.MEDIUM

        # --- Job removed ---
        if change.before is not None and change.after is None:
            return Severity.MEDIUM

        # --- Modified job ---
        if change.before and change.after:
            # Salary change is always high signal
            if any(sc.job_id == job_id for sc in trends.salary_changes):
                return Severity.HIGH

            # Title change depends on persistence
            if any(tc.job_id == job_id for tc in trends.title_changes):
                if job_id in trends.persistent_jobs:
                    return Severity.HIGH
                return Severity.MEDIUM

            # Any other change on a persistent job
            if job_id in trends.persistent_jobs:
                return Severity.MEDIUM

        return Severity.LOW
