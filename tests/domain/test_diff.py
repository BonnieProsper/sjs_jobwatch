from datetime import date

from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.job import Job


def test_added_job_change():
    today = date.today()

    job = Job(
        id="1",
        title="Software Engineer",
        employer="TestCorp",
        summary="Summary",
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
    )

    change = JobChange(
        job_id=job.id,
        before=None,
        after=job,
        changes=[],
    )

    assert change.before is None
    assert change.after is job
