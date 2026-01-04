from __future__ import annotations

from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sjs_sitewatch.domain.diff import JobChange


_TEMPLATE_DIR = Path(__file__).parent / "templates"


class AlertRenderer:
    """
    Responsible solely for rendering alert content (text + HTML).
    No SMTP, no filtering, no side effects.
    """

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_subject(self, changes: Iterable[JobChange]) -> str:
        count = len(list(changes))
        return f"SJS SiteWatch — {count} job update(s)"

    def render_text(self, changes: Iterable[JobChange]) -> str:
        template = self._env.get_template("alert_email.txt")
        return template.render(changes=list(changes))

    def render_html(self, changes: Iterable[JobChange]) -> str:
        template = self._env.get_template("alert_email.html")
        return template.render(changes=list(changes))
