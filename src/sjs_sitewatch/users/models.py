from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sjs_sitewatch.alerts.severity import Severity


@dataclass(frozen=True)
class AlertSubscription:
    email: str
    ict_only: bool = True
    region: Optional[str] = None
    frequency: str = "daily"
    hour: int = 12
    min_severity: Severity = Severity.MEDIUM

    def validate(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email address")

        if self.frequency not in {"daily", "weekly"}:
            raise ValueError("Frequency must be 'daily' or 'weekly'")

        if not (0 <= self.hour <= 23):
            raise ValueError("Hour must be between 0 and 23")
