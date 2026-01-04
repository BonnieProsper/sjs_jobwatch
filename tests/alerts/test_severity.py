from datetime import date

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.explain import ChangeSeverity, job_change_severity
from sjs_sitewatch.domain.job import Job


def _job(**overrides) -> Job:
    today = date.today()

    return Job(
        id="1",
        title="Software Engineer",
        employer="Corp",
        summary="Test",
        description="Desc",
        category="ICT",
        classification="IT",
        sub_classification="Software",
        job_type="Full Time",
        region="Auckland",
        area="Remote",
        pay_min=100000,
        pay_max=120000,
        posted_date=today,
        start_date=None,
        end_date=None,
        **overrides,
    )


def test_new_job_is_at_least_medium_severity():
    job = _job()

    change = JobChange(
        job_id=job.id,
        before=None,
        after=job,
        changes=[],
    )

    severity = job_change_severity(change)
    assert severity >= ChangeSeverity.MEDIUM


def test_no_change_is_low_severity():
    before = _job()
    after = _job()

    change = JobChange(
        job_id=after.id,
        before=before,
        after=after,
        changes=[],
    )

    assert job_change_severity(change) == ChangeSeverity.LOW
