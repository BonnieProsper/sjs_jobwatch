from __future__ import annotations

from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.sinks.base import AlertSink


class AlertDeliveryService:
    """
    Fan-out delivery for scored alerts.

    This class is responsible for:
    - accepting final ScoredChange objects
    - dispatching them to one or more sinks

    No business logic, no filtering.
    """

    def __init__(self, sinks: Iterable[AlertSink]) -> None:
        self._sinks = list(sinks)

    def deliver(self, changes: list[ScoredChange]) -> None:
        if not changes:
            return

        for sink in self._sinks:
            sink.send(changes)
