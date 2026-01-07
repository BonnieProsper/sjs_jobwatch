from pathlib import Path

from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from tests.helpers.jobs import make_job


SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


def normalize_html(html: str) -> str:
    """
    Normalize whitespace so tests are robust to formatting.
    """
    return " ".join(html.split())


def test_render_html_modified_job_snapshot() -> None:
    renderer = AlertRenderer()

    before = make_job(
        id="job-1",
        title="Junior Developer",
    )
    after = make_job(
        id="job-1",
        title="Senior Developer",
    )

    change = JobChange(
        job_id="job-1",
        before=before,
        after=after,
        changes=[
            FieldChange(
                field="title",
                before="Junior Developer",
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

    html = renderer.render_html(changes)

    snapshot = (SNAPSHOTS_DIR / "email_modified_job.html").read_text(
        encoding="utf-8"
    )
    print(renderer.render_html(changes))
    assert normalize_html(html) == normalize_html(snapshot)
 
