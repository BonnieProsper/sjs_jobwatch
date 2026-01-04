from __future__ import annotations

import json
from pathlib import Path
from typing import List

from state.models import Snapshot


SNAPSHOT_DIR = Path("snapshots")
SNAPSHOT_DIR.mkdir(exist_ok=True)


def _snapshot_path(timestamp: str) -> Path:
    return SNAPSHOT_DIR / f"{timestamp}.json"


def save_snapshot(snapshot: Snapshot) -> None:
    path = _snapshot_path(snapshot.meta.captured_at)
    path.write_text(
        json.dumps(snapshot.to_dict(), indent=2),
        encoding="utf-8",
    )


def load_all_snapshots() -> List[Snapshot]:
    snapshots: List[Snapshot] = []

    for path in sorted(SNAPSHOT_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        snapshots.append(Snapshot.from_dict(raw))

    return snapshots


def load_latest_snapshot() -> Snapshot | None:
    snapshots = load_all_snapshots()
    return snapshots[-1] if snapshots else None
