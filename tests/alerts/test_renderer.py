from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange

from helpers.jobs import make_job


def test_html_snapshot(snapshot):
    renderer = AlertRenderer()

    job = make_job(
        id="job-1",
        title="Data Engineer",
    )

    change = ScoredChange(
        change=JobChange(
            job_id=job.id,
            before=None,
            after=job,
            changes=[],
        ),
        severity=Severity.HIGH,
    )

    html = renderer.render_html([change])

    snapshot.assert_match(html, "alert_email.html")
