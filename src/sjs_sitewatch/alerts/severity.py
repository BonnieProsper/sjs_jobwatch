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

    Severity rules are explicit, conservative, and test-driven.
    """

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> Severity:
        job_id = change.job_id

        # --- Job added ---
        # New jobs are always high signal
        if change.before is None and change.after is not None:
            return Severity.HIGH

        # --- Job removed ---
        if change.before is not None and change.after is None:
            return Severity.MEDIUM

        # --- Modified job ---
        if change.before and change.after:
            # Salary changes are always high signal
            if any(sc.job_id == job_id for sc in trends.salary_changes):
                return Severity.HIGH

            # Title changes escalate if job persists over time
            if any(tc.job_id == job_id for tc in trends.title_changes):
                if job_id in trends.persistent_jobs:
                    return Severity.HIGH
                return Severity.MEDIUM

            # Any change to a persistent job is medium signal
            if job_id in trends.persistent_jobs:
                return Severity.MEDIUM

        return Severity.LOW
