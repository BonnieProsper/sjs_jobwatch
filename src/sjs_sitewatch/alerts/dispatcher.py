from typing import List

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription

__all__ = [
    "dispatch_alert",
    "AlertDispatcher",
]


class AlertDispatcher:
    """
    Converts raw diffs into scored alert changes.
    """

    def __init__(self) -> None:
        self._severity = SeverityCalculator()

    def dispatch(
        self,
        diff: DiffResult,
        trends: TrendReport,
    ) -> List[ScoredChange]:
        scored: List[ScoredChange] = []

        for change in diff.added + diff.removed + diff.modified:
            severity = self._severity.score(change, trends)
            scored.append(
                ScoredChange(
                    change=change,
                    severity=severity,
                )
            )

        return scored

    def filter_min_severity(
        self,
        changes: list[ScoredChange],
        min_severity: Severity,
    ) -> list[ScoredChange]:
        filtered: list[ScoredChange] = []

        for c in changes:
            # New jobs are never delivered to HIGH-only subscriptions
            if (
                min_severity == Severity.HIGH
                and c.change.before is None
                and c.change.after is not None
            ):
                continue

            if c.severity >= min_severity:
                filtered.append(c)

        return filtered


# -------------------------------------------------
# Public convenience API (stable entry point)
# -------------------------------------------------

def dispatch_alert(
    *,
    diff: DiffResult,
    trends: TrendReport,
    subscription: AlertSubscription,
) -> List[ScoredChange]:
    """
    High-level alert dispatch entry point.

    - scores changes
    - applies subscription severity filter
    """

    dispatcher = AlertDispatcher()
    scored = dispatcher.dispatch(diff=diff, trends=trends)

    return dispatcher.filter_min_severity(
        scored,
        subscription.min_severity,
    )
