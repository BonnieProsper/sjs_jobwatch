from __future__ import annotations

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


def send_email_alert(
    *,
    diff: DiffResult,
    trends: TrendReport,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    """
    Backwards-compatible email alert API.

    Delegates to EmailSink.
    """
    pipeline = AlertPipeline()
    changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

    EmailSink(
        to_email=subscription.email,
        dry_run=dry_run,
    ).send(changes)
