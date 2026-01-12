from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange

from tests.helpers.jobs import make_job


def test_email_sink_dry_run_outputs_message(capsys) -> None:
    before = make_job(id="job-1", title="Dev")
    after = make_job(id="job-1", title="Senior Dev")

    change = ScoredChange(
        change=JobChange(
            job_id="job-1",
            before=before,
            after=after,
            changes=[],
        ),
        severity=Severity.HIGH,
        reason="Title changed",
    )

    sink = EmailSink(
        to_email="test@example.com",
        dry_run=True,
    )

    sink.send([change])

    output = capsys.readouterr().out

    assert "EMAIL (dry run)" in output
    assert "Senior Dev" in output
