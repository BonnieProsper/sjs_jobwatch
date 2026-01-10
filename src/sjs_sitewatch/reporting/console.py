from __future__ import annotations

from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.severity import Severity


def print_alerts(changes: Iterable[ScoredChange]) -> None:
    """
    Print alert output to console using the same rendering
    and severity logic as email alerts.
    """
    changes = list(changes)

    if not changes:
        print("No significant changes detected.")
        return

    renderer = AlertRenderer()
    print(renderer.render_text(changes))


def print_severity_summary(changes: Iterable[ScoredChange]) -> None:
    """
    One-line severity summary (useful for cron).
    """
    counts = {
        Severity.HIGH: 0,
        Severity.MEDIUM: 0,
        Severity.LOW: 0,
    }

    for c in changes:
        counts[c.severity] += 1

    print(
        f"HIGH: {counts[Severity.HIGH]} | "
        f"MEDIUM: {counts[Severity.MEDIUM]} | "
        f"LOW: {counts[Severity.LOW]}"
    )
