from __future__ import annotations

import json
from pathlib import Path
from typing import List

from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.alerts.severity import Severity


class SubscriptionStore:
    """
    Simple JSON-backed storage for alert subscriptions.
    """

    def __init__(self, path: Path):
        self.path = path

    def load_all(self) -> List[AlertSubscription]:
        if not self.path.exists():
            return []

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        subs: list[AlertSubscription] = []

        for item in raw:
            severity_value = item.get("min_severity", Severity.MEDIUM.value)
            item["min_severity"] = Severity(severity_value)
            sub = AlertSubscription(**item)
            sub.validate()
            subs.append(sub)

        return subs

    def save_all(self, subs: List[AlertSubscription]) -> None:
        payload = [
            {
                "email": sub.email,
                "ict_only": sub.ict_only,
                "region": sub.region,
                "frequency": sub.frequency,
                "hour": sub.hour,
                "min_severity": sub.min_severity.name,
            }
            for sub in subs
        ]

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
