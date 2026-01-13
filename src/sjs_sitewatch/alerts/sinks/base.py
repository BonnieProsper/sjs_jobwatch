from __future__ import annotations

from abc import ABC, abstractmethod

from sjs_sitewatch.alerts.models import ScoredChange


class AlertSink(ABC):
    """
    Delivery endpoint for alerts (email, console, slack, etc).
    """

    @abstractmethod
    def send(self, changes: list[ScoredChange]) -> None:
        raise NotImplementedError
