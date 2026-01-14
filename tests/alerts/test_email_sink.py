import logging

from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from tests.helpers.jobs import make_job


def test_email_sink_dry_run_logs_message(caplog):
    before = make_job(title="Developer")
    after = make_job(title="Senior Developer")

    change = ScoredChange(
        change=JobChange(
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
        ),
        severity=Severity.MEDIUM,
        reason="Title changed",
    )

    sink = EmailSink(
        to_email="test@example.com",
        dry_run=True,
    )

    with caplog.at_level(logging.INFO):
        sink.send([change])

    assert "Dry-run email to test@example.com" in caplog.text
    assert "Senior Developer" in caplog.text
