from __future__ import annotations

from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.users.models import AlertSubscription


class ConsoleSink:
    """
    Human-readable console output.
    """

    def send(
        self,
        changes: Iterable[ScoredChange],
        *,
        subscription: AlertSubscription | None = None,
    ) -> None:
        changes = list(changes)

        if not changes:
            print("No significant changes detected.")
            return

        for c in changes:
            print(
                f"[{c.severity.name}] "
                f"{c.change.job_id} — {c.reason}"
            )

        self._print_summary(changes)

    def _print_summary(self, changes: list[ScoredChange]) -> None:
        counts = {
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
        }

        for c in changes:
            counts[c.severity] += 1

        print(
            f"\nSummary: "
            f"HIGH={counts[Severity.HIGH]}, "
            f"MEDIUM={counts[Severity.MEDIUM]}, "
            f"LOW={counts[Severity.LOW]}"
        )
