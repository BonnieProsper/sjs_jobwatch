from __future__ import annotations

from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import SeverityCalculator
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.trends import TrendReport

__all__ = ["AlertScorer"]


class AlertScorer:
    """
    Converts domain-level job changes into scored alert changes.

    Responsibilities:
    - Combine diff changes into a single stream
    - Apply severity scoring
    - Attach human-readable explanations

    This class is:
    - Pure (no I/O)
    - Deterministic
    - Independent of subscriptions and sinks
    """

    def __init__(
        self,
        severity_calculator: SeverityCalculator | None = None,
    ) -> None:
        self._severity = severity_calculator or SeverityCalculator()

    def score_all(
        self,
        *,
        diff: DiffResult,
        trends: TrendReport,
    ) -> list[ScoredChange]:
        """
        Score all changes contained in a diff result.
        """
        changes = self._flatten_diff(diff)

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

    @staticmethod
    def _flatten_diff(diff: DiffResult) -> Iterable[JobChange]:
        """
        Return all job changes in a stable, predictable order.
        """
        return (
            diff.added
            + diff.removed
            + diff.modified
        )
