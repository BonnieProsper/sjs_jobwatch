
from sjs_sitewatch.domain.diff import JobChange
from tests.helpers.jobs import make_job


def test_added_job_change() -> None:
    job = make_job(
        id="1",
        title="Software Engineer",
    )

    change = JobChange(
        job_id=job.id,
        before=None,
        after=job,
        changes=[],
    )

    assert change.before is None
    assert change.after == job
    assert change.job_id == "1"
