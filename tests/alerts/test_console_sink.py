from sjs_sitewatch.alerts.sinks.console import ConsoleSink
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange

from tests.helpers.jobs import make_job


def test_console_sink_outputs_summary(capsys) -> None:
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

    ConsoleSink().send([change])

    output = capsys.readouterr().out

    assert "HIGH" in output
    assert "job-1" in output
    assert "Summary:" in output
