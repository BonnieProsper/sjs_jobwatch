from datetime import date

from sjs_sitewatch.alerts.filters import is_ict_job
from sjs_sitewatch.domain.job import Job


def _job(category: str) -> Job:
    today = date.today()

    return Job(
        id="1",
        title="Test",
        employer="Corp",
        summary="Summary",
        description="Desc",
        category=category,
        classification="IT",
        sub_classification="General",
        job_type="Full Time",
        region="Auckland",
        area="Remote",
        pay_min=100000,
        pay_max=120000,
        posted_date=today,
        start_date=None,
        end_date=None,
    )


def test_is_ict_job():
    assert is_ict_job(_job("ICT")) is True
    assert is_ict_job(_job("Health")) is False
