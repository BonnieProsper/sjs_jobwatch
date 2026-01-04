from enum import IntEnum

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.trends import TrendReport


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SeverityCalculator:
    """
    Determine how important a job change is.

    Severity is derived from:
    - type of change (added / removed / modified)
    - historical persistence
    - salary or title signals
    """

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> Severity:
        # New job postings are always high signal
        if change.before is None and change.after is not None:
            return Severity.HIGH
        
        # --- Removed jobs are usually medium signal ---
        if change.before is not None and change.after is None:
            return Severity.MEDIUM

        # --- Modified jobs ---
        if change.before and change.after:
            job_id = change.job_id

            # Salary change is always high signal
            for salary_change in trends.salary_changes:
                if salary_change.job_id == job_id:
                    return Severity.HIGH

            # Title change is medium → high depending on persistence
            for title_change in trends.title_changes:
                if title_change.job_id == job_id:
                    if job_id in trends.persistent_jobs:
                        return Severity.HIGH
                    return Severity.MEDIUM

            # Persistent job with any modification
            if job_id in trends.persistent_jobs:
                return Severity.MEDIUM

        # --- Default fallback ---
        return Severity.LOW


# TODO: new, consolidate both files

from enum import IntEnum

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.trends import TrendReport


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SeverityCalculator:
    """
    Assigns severity to a JobChange using both:
    - local diff information
    - multi-day trend context
    """

    def score(
        self,
        change: JobChange,
        trends: TrendReport,
    ) -> Severity:
        # Job added or removed is always notable
        if change.before is None or change.after is None:
            return Severity.HIGH

        # Title or salary change
        if any(
            c.field in {"title", "pay_min", "pay_max"}
            for c in change.changes
        ):
            return Severity.HIGH

        # Persistent jobs changing is more important
        if change.job_id in trends.persistent_jobs:
            return Severity.MEDIUM

        return Severity.LOW
