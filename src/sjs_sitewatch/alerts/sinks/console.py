from __future__ import annotations

import logging
from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.users.models import AlertSubscription

log = logging.getLogger(__name__)


class ConsoleSink:
    """
    Human-readable console output sink.
    """

    def send(
        self,
        changes: Iterable[ScoredChange],
        *,
        subscription: AlertSubscription | None = None,
    ) -> None:
        changes = list(changes)

        if not changes:
            log.info("No significant changes detected.")
            return

        for c in changes:
            log.info(
                "[%s] %s — %s",
                c.severity.name,
                c.change.job_id,
                c.reason,
            )

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
