from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.domain.diff import DiffResult, JobChange, FieldChange
from sjs_sitewatch.domain.job import Job

from datetime import date


def make_job(
    *,
    id: str = "job-1",
    title: str = "Software Engineer",
    employer: str | None = "Test Employer",
    summary: str | None = "Summary",
    description: str | None = "Description",
    category: str | None = "ICT",
    classification: str | None = "IT",
    sub_classification: str | None = "Software",
    job_type: str | None = "Full time",
    region: str | None = "Auckland",
    area: str | None = "CBD",
    pay_min: float | None = 90000,
    pay_max: float | None = 120000,
    posted_date: date | None = date(2025, 1, 1),
    start_date: date | None = None,
    end_date: date | None = None,
) -> Job:
    return Job(
        id=id,
        title=title,
        employer=employer,
        summary=summary,
        description=description,
        category=category,
        classification=classification,
        sub_classification=sub_classification,
        job_type=job_type,
        region=region,
        area=area,
        pay_min=pay_min,
        pay_max=pay_max,
        posted_date=posted_date,
        start_date=start_date,
        end_date=end_date,
    )


def test_send_email_alert_dry_run_modified_job(capsys):
    before = _make_job("job-1", "Developer")
    after = _make_job("job-1", "Senior Developer")

    diff = DiffResult(
        added=[],
        removed=[],
        modified=[
            JobChange(
                job_id="job-1",
                before=before,
                after=after,
                changes=[
                    FieldChange(
                        field="title",
                        before="Developer",
                        after="Senior Developer",
                    )
                ],
            )
        ],
    )

    send_email_alert(
        diff=diff,
        to_email="test@example.com",
        dry_run=True,
    )

    output = capsys.readouterr().out
    assert "EMAIL (dry run)" in output
    assert "Senior Developer" in output
