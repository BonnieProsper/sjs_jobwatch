from __future__ import annotations

from typing import List

from sjs_sitewatch.alerts.scorer import AlertScorer
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


ICT_CATEGORY = "ICT"


class AlertPipeline:
    """
    Deterministic alert orchestration.

    Responsibilities:
    - Apply severity scoring
    - Apply subscription-level filtering
    - Produce final ScoredChange list

    No I/O.
    """

    def __init__(self) -> None:
        self._scorer = AlertScorer()

    def run(
        self,
        *,
        diff: DiffResult,
        trends: TrendReport,
        subscription: AlertSubscription,
    ) -> List[ScoredChange]:
        scored = self._scorer.score_all(
            diff=diff,
            trends=trends,
        )

        scored = [
            c for c in scored
            if c.severity >= subscription.min_severity
        ]

        if subscription.region:
            scored = [
                c for c in scored
                if c.change.after
                and c.change.after.region == subscription.region
            ]

        if subscription.ict_only:
            scored = [
                c for c in scored
                if c.change.after
                and c.change.after.category == ICT_CATEGORY
            ]   

        return scored
