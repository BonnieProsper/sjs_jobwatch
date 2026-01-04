from typing import Iterable, List

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport


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
        changes: Iterable[ScoredChange],
        min_severity: Severity,
    ) -> List[ScoredChange]:
        return [c for c in changes if c.severity >= min_severity]
