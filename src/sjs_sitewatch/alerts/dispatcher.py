from typing import Iterable, List

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription

__all__ = [
    "dispatch_alert",
    "AlertDispatcher",
]


class AlertDispatcher:
    """
    Converts domain diffs into scored alert changes and applies
    subscription-level delivery rules.

    Responsibilities:
    - invoke severity scoring
    - carry explanations forward
    - apply subscription filters

    This class contains no I/O and no formatting logic.
    """

    def __init__(self, severity_calculator: SeverityCalculator | None = None) -> None:
        self._severity = severity_calculator or SeverityCalculator()

    # -------------------------------------------------
    # Scoring
    # -------------------------------------------------

    def score_changes(
        self,
        changes: Iterable[JobChange],
        trends: TrendReport,
    ) -> list[ScoredChange]:
        """
        Assign severity and explanation to a sequence of JobChange objects.
        """
        scored: list[ScoredChange] = []

        for change in changes:
            severity, reason = self._severity.score_with_reason(
                change=change,
                trends=trends,
            )

            scored.append(
                ScoredChange(
                    change=change,
                    severity=severity,
                    reason=reason,
                )
            )

        return scored

    def dispatch(
        self,
        diff: DiffResult,
        trends: TrendReport,
    ) -> list[ScoredChange]:
        """
        Convert a DiffResult into scored alert changes.
        """
        all_changes = (
            diff.added
            + diff.removed
            + diff.modified
        )

        return self.score_changes(
            changes=all_changes,
            trends=trends,
        )

    # -------------------------------------------------
    # Filtering
    # -------------------------------------------------

    def filter_min_severity(
        self,
        changes: Iterable[ScoredChange],
        min_severity: Severity,
    ) -> list[ScoredChange]:
        """
        Apply subscription severity delivery rules.

        Note:
        - HIGH-only subscriptions do not receive new-job alerts
          to avoid high-volume noise.
        """
        filtered: list[ScoredChange] = []

        for scored in changes:
            if self._is_excluded_new_job(scored, min_severity):
                continue

            if scored.severity >= min_severity:
                filtered.append(scored)

        return filtered

    @staticmethod
    def _is_excluded_new_job(
        scored: ScoredChange,
        min_severity: Severity,
    ) -> bool:
        """
        Determine whether a scored change should be excluded due
        to subscription delivery rules.
        """
        is_new_job = (
            scored.change.before is None
            and scored.change.after is not None
        )

        return (
            min_severity == Severity.HIGH
            and is_new_job
        )


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

    Responsibilities:
    - score changes
    - apply subscription severity filtering

    This function is intentionally stable.
    """
    dispatcher = AlertDispatcher()

    scored = dispatcher.dispatch(
        diff=diff,
        trends=trends,
    )

    return dispatcher.filter_min_severity(
        scored,
        subscription.min_severity,
    )
