from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.users.models import AlertSubscription


def test_email_sink_dry_run_does_not_error(sample_snapshots):
    prev, curr = sample_snapshots

    diff = diff_snapshots(prev.jobs, curr.jobs)
    trends = TrendAnalyzer([prev, curr]).analyze()

    subscription = AlertSubscription(
        email="test@example.com",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    send_email_alert(
        diff=diff,
        trends=trends,
        subscription=subscription,
        dry_run=True,
    )
