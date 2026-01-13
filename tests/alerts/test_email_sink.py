import io
from contextlib import redirect_stdout

from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from tests.helpers.jobs import make_job


def test_email_sink_dry_run_outputs_message():
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

    buf = io.StringIO()
    with redirect_stdout(buf):
        sink.send([change])

    output = buf.getvalue()
    assert "EMAIL (dry run)" in output
    assert "Senior Developer" in output
