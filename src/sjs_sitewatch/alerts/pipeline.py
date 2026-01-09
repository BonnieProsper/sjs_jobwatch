from __future__ import annotations

from typing import List

from sjs_sitewatch.alerts.dispatcher import AlertDispatcher
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


class AlertPipeline:
    """
    Canonical alert orchestration pipeline.

    Responsibilities:
    - Apply severity scoring
    - Apply subscription-level filtering
    - Produce final ScoredChange list

    This class contains NO I/O and is fully deterministic.
    """

    def __init__(self) -> None:
        self._dispatcher = AlertDispatcher()

    def run(
        self,
        *,
        diff: DiffResult,
        trends: TrendReport,
        subscription: AlertSubscription,
    ) -> List[ScoredChange]:
        scored = self._dispatcher.dispatch(diff, trends)

        # -------------------------
        # Severity filtering
        # -------------------------
        scored = [
            c for c in scored
            if c.severity >= subscription.min_severity
        ]

        # -------------------------
        # Region filtering
        # -------------------------
        if subscription.region:
            scored = [
                c for c in scored
                if (
                    c.change.after
                    and c.change.after.region == subscription.region
                )
            ]

        # -------------------------
        # ICT-only filtering
        # -------------------------
        if subscription.ict_only:
            scored = [
                c for c in scored
                if (
                    c.change.after
                    and c.change.after.category == "ICT"
                )
            ]

        return scored

# TODO: ADD (where?): ICT_CATEGORY = "ICT"
