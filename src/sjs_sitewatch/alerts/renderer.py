from __future__ import annotations

from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity


_TEMPLATE_DIR = Path(__file__).parent / "templates"


class AlertRenderer:
    """
    Pure renderer for alert content (text + HTML).
    No side effects.
    """

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_subject(self, changes: Iterable[ScoredChange]) -> str:
        changes = list(changes)
        highest = max((c.severity for c in changes), default=Severity.LOW)

        return (
            f"SJS SiteWatch — "
            f"{len(changes)} update(s) "
            f"[{highest.name}]"
        )

    def render_text(self, changes: Iterable[ScoredChange]) -> str:
        template = self._env.get_template("alert_email.txt")
        return template.render(changes=list(changes))

    def render_html(self, changes: Iterable[ScoredChange]) -> str:
        template = self._env.get_template("alert_email.html")
        return template.render(changes=list(changes))
