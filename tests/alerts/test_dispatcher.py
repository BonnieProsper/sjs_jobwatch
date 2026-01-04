from datetime import date

from sjs_sitewatch.alerts.dispatcher import dispatch_alert
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.users.models import AlertSubscription


def test_dispatcher_dry_run_does_not_crash(capsys) -> None:
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
        email="dryrun@example.com",
        ict_only=True,
        region=None,
    )

    dispatch_alert(
        diff=diff,
        subscription=subscription,
        dry_run=True,
    )

    captured = capsys.readouterr()
    assert "SJS SiteWatch" in captured.out or captured.err == ""
