from datetime import datetime, timezone, date

from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import (
    total_jobs,
    job_growth,
    region_growth,
    rolling_job_growth,
    rolling_churn,
)



# Test helpers
def make_job(
    *,
    id: str,
    title: str,
    region: str,
) -> Job:
    """Create a valid Job with sane defaults for tests."""
    today = date.today()

    return Job(
        id=id,
        title=title,
        employer="Test Employer",
        summary="Test summary",
        description="Test description",
        category="ICT",
        classification="Information Technology",
        sub_classification="Software Engineering",
        job_type="Full Time",
        area="Test Area",
        pay_min=100000.0,
        pay_max=120000.0,
        posted_date=today,
        start_date=None,
        end_date=None,
        region=region,
    )


def make_snapshot(jobs: list[Job]) -> Snapshot:
    return Snapshot(
        jobs={job.id: job for job in jobs},
        captured_at=datetime.now(tz=timezone.utc),
    )


# TESTS
def test_total_jobs():
    snap = make_snapshot([
        make_job(id="1", title="A", region="NZ"),
        make_job(id="2", title="B", region="AU"),
    ])

    assert total_jobs(snap) == 2


def test_job_growth():
    prev = make_snapshot([
        make_job(id="1", title="A", region="NZ"),
    ])

    curr = make_snapshot([
        make_job(id="1", title="A", region="NZ"),
        make_job(id="2", title="B", region="NZ"),
    ])

    assert job_growth(prev, curr) == 1


def test_region_growth():
    prev = make_snapshot([
        make_job(id="1", title="A", region="NZ"),
        make_job(id="2", title="B", region="NZ"),
    ])

    curr = make_snapshot([
        make_job(id="1", title="A", region="NZ"),
        make_job(id="2", title="B", region="AU"),
        make_job(id="3", title="C", region="AU"),
    ])

    assert region_growth(prev, curr) == {
        "NZ": -1,
        "AU": 2,
    }


def test_rolling_job_growth():
    snapshots = [
        make_snapshot([]),
        make_snapshot([
            make_job(id="1", title="A", region="NZ"),
        ]),
        make_snapshot([
            make_job(id="1", title="A", region="NZ"),
            make_job(id="2", title="B", region="NZ"),
        ]),
    ]

    assert rolling_job_growth(snapshots, days=1) == 1


def test_rolling_churn():
    snapshots = [
        make_snapshot([]),
        make_snapshot([
            make_job(id="1", title="A", region="NZ"),
        ]),
        make_snapshot([]),
    ]

    assert rolling_churn(snapshots) == 2
