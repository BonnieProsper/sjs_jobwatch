from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from tests.helpers.jobs import make_job


def test_email_sink_dry_run_prints_content(capsys):
    before = make_job(id="job-1", title="Developer")
    after = make_job(id="job-1", title="Senior Developer")

    change = JobChange(
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

    changes = [
        ScoredChange(
            change=change,
            severity=Severity.HIGH,
        )
    ]

    sink = EmailSink(
        to_email="test@example.com",
        dry_run=True,
    )

    sink.send(changes)

    out = capsys.readouterr().out
    assert "EMAIL (dry run)" in out
    assert "Senior Developer" in out
