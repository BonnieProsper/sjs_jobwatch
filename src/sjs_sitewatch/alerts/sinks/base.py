from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange


class AlertSink(ABC):
    """
    Output sink for scored alert changes.

    Sinks perform I/O only.
    They do NOT score, filter, or transform alert meaning.
    """

    @abstractmethod
    def send(self, changes: Iterable[ScoredChange]) -> None:
        ...
