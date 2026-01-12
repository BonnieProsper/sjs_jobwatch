# TODO - use helper etc
from datetime import date

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.users.models import AlertSubscription


def _job(**kwargs) -> Job:
    return Job(
        id=kwargs.get("id", "1"),
        title=kwargs.get("title", "Developer"),
        employer=kwargs.get("employer", "Org"),
        region=kwargs.get("region", "Wellington"),
        area=kwargs.get("area", "IT"),
        salary=kwargs.get("salary", "100k"),
        posted=kwargs.get("posted", date.today()),
    )


def test_new_job_triggers_high_severity():
    old = Snapshot(date(2024, 1, 1), jobs=[])
    new = Snapshot(date(2024, 1, 2), jobs=[_job(id="1")])

    diff = diff_snapshots(old.jobs, new.jobs)
    trends = TrendAnalyzer([old, new]).analyze()

    subscription = AlertSubscription(
        email="test@example.com",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    pipeline = AlertPipeline()
    changes = pipeline.run(diff=diff, trends=trends, subscription=subscription)

    assert len(changes) == 1
    assert changes[0].severity == Severity.HIGH
    assert "New job" in changes[0].reason


def test_min_severity_filters_changes():
    old = Snapshot(date(2024, 1, 1), jobs=[_job(id="1", salary="90k")])
    new = Snapshot(date(2024, 1, 2), jobs=[_job(id="1", salary="95k")])

    diff = diff_snapshots(old.jobs, new.jobs)
    trends = TrendAnalyzer([old, new]).analyze()

    subscription = AlertSubscription(
        email="test@example.com",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.HIGH,
    )

    pipeline = AlertPipeline()
    changes = pipeline.run(diff=diff, trends=trends, subscription=subscription)

    # salary change is HIGH only if persistent; otherwise filtered
    assert all(c.severity >= Severity.HIGH for c in changes)
