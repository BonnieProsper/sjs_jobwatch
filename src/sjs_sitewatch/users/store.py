from __future__ import annotations

import json
from pathlib import Path
from typing import List

from sjs_sitewatch.users.models import AlertSubscription


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
        subs = [AlertSubscription(**item) for item in raw]

        for sub in subs:
            sub.validate()

        return subs

    def save_all(self, subs: List[AlertSubscription]) -> None:
        payload = [sub.__dict__ for sub in subs]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
