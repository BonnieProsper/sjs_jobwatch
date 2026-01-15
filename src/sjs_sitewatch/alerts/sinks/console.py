from __future__ import annotations

import logging
from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity

log = logging.getLogger(__name__)


class ConsoleSink:
    """
    Human-readable console output sink.
    Intended for CLI usage and dry-runs.
    """

    def send(self, changes: Iterable[ScoredChange]) -> None:
        changes = list(changes)

        if not changes:
            log.info("No significant changes detected.")
            return

        for c in changes:
            # Log for structured logs
            log.info(
                "[%s] %s — %s",
                c.severity.name,
                c.change.job_id,
                c.reason,
            )

            # Print for user-visible CLI output (tests rely on this)
            if c.change.after and c.change.after.title:
                print(c.change.after.title)

        self._log_summary(changes)

    def _log_summary(self, changes: list[ScoredChange]) -> None:
        counts = {
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
        }

        for c in changes:
            counts[c.severity] += 1

        log.info(
            "Summary: HIGH=%d, MEDIUM=%d, LOW=%d",
            counts[Severity.HIGH],
            counts[Severity.MEDIUM],
            counts[Severity.LOW],
        )
