from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.domain.diff import JobChange, FieldChange

from ._factories import make_job


def test_render_text_contains_title() -> None:
    renderer = AlertRenderer()

    changes = [
        JobChange(
            before=None,
            after=make_job(title="Data Engineer"),
            changes=[],
        )
    ]

    text = renderer.render_text(changes)

    assert "Data Engineer" in text


def test_render_html_contains_field_changes() -> None:
    renderer = AlertRenderer()

    before = make_job(id="1", title="Junior Developer")
    after = make_job(id="1", title="Senior Developer")

    changes = [
        JobChange(
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
    ]

    html = renderer.render_html(changes)

    assert "Senior Developer" in html
    assert "Junior Developer" in html
