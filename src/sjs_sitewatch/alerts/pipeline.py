from typing import Iterable, List

from sjs_sitewatch.alerts.dispatcher import AlertDispatcher
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


class AlertPipeline:
    """
    End-to-end alert preparation:
    diff -> severity -> subscription filtering
    """

    def __init__(self) -> None:
        self._dispatcher = AlertDispatcher()

    def prepare_for_subscription(
        self,
        diff: DiffResult,
        trends: TrendReport,
        subscription: AlertSubscription,
    ) -> List[ScoredChange]:
        scored = self._dispatcher.dispatch(diff, trends)

        # Severity filter
        scored = [
            c for c in scored
            if c.severity >= subscription.min_severity
        ]

        # Region filter (optional)
        if subscription.region:
            scored = [
                c for c in scored
                if (
                    c.change.after
                    and c.change.after.region == subscription.region
                )
            ]

        # ICT-only filter
        if subscription.ict_only:
            scored = [
                c for c in scored
                if (
                    c.change.after
                    and c.change.after.category == "ICT"
                )
            ]

        return scored
