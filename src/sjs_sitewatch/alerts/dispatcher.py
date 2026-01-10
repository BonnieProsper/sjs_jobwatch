from typing import Iterable, List

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import SeverityCalculator
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.trends import TrendReport

__all__ = ["AlertDispatcher"]


class AlertDispatcher:
    """
    Converts domain diffs into scored alert changes.

    Responsibilities:
    - invoke severity scoring
    - attach explanations

    This class contains no I/O and no subscription filtering.
    """

    def __init__(self, severity_calculator: SeverityCalculator | None = None) -> None:
        self._severity = severity_calculator or SeverityCalculator()

    def score_changes(
        self,
        changes: Iterable[JobChange],
        trends: TrendReport,
    ) -> list[ScoredChange]:
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
        all_changes = (
            diff.added
            + diff.removed
            + diff.modified
        )

        return self.score_changes(
            changes=all_changes,
            trends=trends,
        )
