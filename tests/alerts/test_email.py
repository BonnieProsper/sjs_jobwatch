from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import DiffResult, JobChange, FieldChange
from sjs_sitewatch.users.models import AlertSubscription

from tests.helpers.jobs import make_job


def test_email_sink_dry_run_modified_job(capsys):
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

    subscription = AlertSubscription(
        email="test@example.com",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    pipeline = AlertPipeline()
    changes = pipeline.run(
        diff=diff,
        trends=None,  # trends unused by this test
        subscription=subscription,
    )

    EmailSink(
        to_email="test@example.com",
        dry_run=True,
    ).send(changes)

    output = capsys.readouterr().out

    assert "EMAIL (dry run)" in output
    assert "Senior Developer" in output
