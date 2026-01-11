from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.domain.diff import DiffResult, JobChange, FieldChange

from tests.helpers.jobs import make_job


def test_send_email_alert_dry_run_modified_job(capsys):
    before = make_job(
        id="job-1",
        title="Developer",
    )
    after = make_job(
        id="job-1",
        title="Senior Developer",
    )

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

    # TODO
    send_email_alert(
        diff=diff,
        to_email="test@example.com",
        dry_run=True,
    )

    output = capsys.readouterr().out

    assert "EMAIL (dry run)" in output
    assert "Senior Developer" in output
