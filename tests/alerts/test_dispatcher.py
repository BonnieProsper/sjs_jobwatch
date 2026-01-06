from datetime import date

from sjs_sitewatch.alerts.dispatcher import dispatch_alert
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


def _empty_trends() -> TrendReport:
    """
    Minimal valid TrendReport for dispatcher tests.
    Dispatcher does not require historical context for basic scoring.
    """
    return TrendReport(
        job_counts_by_day={},
        persistent_jobs=[],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[],
        salary_changes=[],
    )


def test_dispatch_alert_returns_scored_changes() -> None:
    job = Job(
        id="1",
        title="Data Engineer",
        employer="GovTech",
        summary="Work on data pipelines",
        description=None,
        category="IT",
        classification=None,
        sub_classification=None,
        job_type="Permanent",
        region="Auckland",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=date.today(),
        start_date=None,
        end_date=None,
    )

    diff = DiffResult(
        added=[JobChange("1", None, job, [])],
        removed=[],
        modified=[],
    )

    subscription = AlertSubscription(
        email="test@example.com",
        ict_only=False,
        region=None,
        min_severity=Severity.LOW,
    )

    results = dispatch_alert(
        diff=diff,
        trends=_empty_trends(),
        subscription=subscription,
    )

    assert len(results) == 1
    assert results[0].change.job_id == "1"
    assert results[0].severity >= Severity.LOW


def test_dispatch_alert_applies_min_severity_filter() -> None:
    job = Job(
        id="2",
        title="Junior Clerk",
        employer="Agency",
        summary="Admin work",
        description=None,
        category="Administration",
        classification=None,
        sub_classification=None,
        job_type="Permanent",
        region="Auckland",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=date.today(),
        start_date=None,
        end_date=None,
    )

    diff = DiffResult(
        added=[JobChange("2", None, job, [])],
        removed=[],
        modified=[],
    )

    subscription = AlertSubscription(
        email="filter@example.com",
        ict_only=False,
        region=None,
        min_severity=Severity.HIGH,
    )

    results = dispatch_alert(
        diff=diff,
        trends=_empty_trends(),
        subscription=subscription,
    )

    assert results == []
