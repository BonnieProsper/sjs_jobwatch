import io
from contextlib import redirect_stdout

from sjs_sitewatch.alerts.sinks.console import ConsoleSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from tests.helpers.jobs import make_job


def test_console_sink_prints_alerts():
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
        severity=Severity.HIGH,
        reason="Title upgrade",
    )

    sink = ConsoleSink()

    buf = io.StringIO()
    with redirect_stdout(buf):
        sink.send([change])

    output = buf.getvalue()
    assert "Senior Developer" in output
    assert "HIGH" in output
