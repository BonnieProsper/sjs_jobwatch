from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.alerts.severity import Severity


def test_alert_pipeline_produces_changes(sample_snapshots):
    prev, curr = sample_snapshots

    diff = diff_snapshots(prev.jobs, curr.jobs)
    trends = TrendAnalyzer([prev, curr]).analyze()

    pipeline = AlertPipeline()

    subscription = AlertSubscription(
        email="console",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

    assert isinstance(changes, list)
