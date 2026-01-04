from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict

from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.job import Job


class FilesystemSnapshotStore:
    """
    Append-only filesystem-backed snapshot store.

    Each snapshot is stored as a single JSON file, named by its
    capture timestamp.
    """

    def __init__(self, root: Path) -> None:
        self._root = root
        self._snapshots_dir = root / "snapshots"
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Public API
    # -------------------------

    def save(self, snapshot: Snapshot) -> Path:
        path = self._snapshot_path(snapshot)

        if path.exists():
            raise FileExistsError(f"Snapshot already exists: {path}")

        with path.open("w", encoding="utf-8") as f:
            json.dump(self._serialize_snapshot(snapshot), f, indent=2)

        return path

    def load_all(self) -> list[Snapshot]:
        snapshots: list[Snapshot] = []

        for path in sorted(self._snapshots_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            snapshots.append(self._deserialize_snapshot(payload))

        return snapshots

    def load_latest(self) -> Snapshot | None:
        paths = sorted(self._snapshots_dir.glob("*.json"))
        if not paths:
            return None

        with paths[-1].open("r", encoding="utf-8") as f:
            payload = json.load(f)

        return self._deserialize_snapshot(payload)

    # -------------------------
    # Internal helpers
    # -------------------------

    def _snapshot_path(self, snapshot: Snapshot) -> Path:
        ts = snapshot.captured_at.isoformat(timespec="seconds")
        safe = ts.replace(":", "-")
        return self._snapshots_dir / f"{safe}.json"

    @staticmethod
    def _serialize_snapshot(snapshot: Snapshot) -> Dict[str, Any]:
        return {
            "captured_at": snapshot.captured_at.isoformat(),
            "jobs": {
                job_id: FilesystemSnapshotStore._serialize_job(job)
                for job_id, job in snapshot.jobs.items()
            },
        }

    @staticmethod
    def _deserialize_snapshot(payload: Dict[str, Any]) -> Snapshot:
        return Snapshot(
            captured_at=datetime.fromisoformat(payload["captured_at"]),
            jobs={
                job_id: FilesystemSnapshotStore._deserialize_job(job_payload)
                for job_id, job_payload in payload["jobs"].items()
            },
        )

    @staticmethod
    def _serialize_job(job: Job) -> Dict[str, Any]:
        return {
            "id": job.id,
            "title": job.title,
            "employer": job.employer,
            "summary": job.summary,
            "description": job.description,
            "category": job.category,
            "classification": job.classification,
            "sub_classification": job.sub_classification,
            "job_type": job.job_type,
            "region": job.region,
            "area": job.area,
            "pay_min": job.pay_min,
            "pay_max": job.pay_max,
            "posted_date": _serialize_date(job.posted_date),
            "start_date": _serialize_date(job.start_date),
            "end_date": _serialize_date(job.end_date),
        }

    @staticmethod
    def _deserialize_job(payload: Dict[str, Any]) -> Job:
        return Job(
            id=payload["id"],
            title=payload["title"],
            employer=payload.get("employer"),
            summary=payload.get("summary"),
            description=payload.get("description"),
            category=payload.get("category"),
            classification=payload.get("classification"),
            sub_classification=payload.get("sub_classification"),
            job_type=payload.get("job_type"),
            region=payload.get("region"),
            area=payload.get("area"),
            pay_min=payload.get("pay_min"),
            pay_max=payload.get("pay_max"),
            posted_date=_deserialize_date(payload.get("posted_date")),
            start_date=_deserialize_date(payload.get("start_date")),
            end_date=_deserialize_date(payload.get("end_date")),
        )


# -------------------------
# Date helpers
# -------------------------

def _serialize_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _deserialize_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None
