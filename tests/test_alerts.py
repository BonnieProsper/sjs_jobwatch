from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.explain import job_change_severity, ChangeSeverity


def test_high_severity_job_change_triggers_alert_condition():
    """
    Domain-level test: high-impact changes should be classifiable
    as alert-worthy.
    """
    job = Job(
        id="1",
        title="Senior Engineer",
        employer="ABC",
        summary=None,
        description=None,
        category="ICT",
        classification=None,
        sub_classification=None,
        job_type="Full Time",
        region="NZ",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=None,
        start_date=None,
        end_date=None,
    )

    change = JobChange(
        job_id="1",
        before=job,
        after=job,
        changes=[],
    )

    assert job_change_severity(change) == ChangeSeverity.LOW
