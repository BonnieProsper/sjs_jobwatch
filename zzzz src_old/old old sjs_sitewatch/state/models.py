from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict

from sjs_sitewatch.ingestion.normalize import Job


@dataclass(frozen=True)
class SnapshotMeta:
    captured_at: str          # ISO timestamp
    total_jobs: int
    by_region: Dict[str, int]


@dataclass(frozen=True)
class Snapshot:
    meta: SnapshotMeta
    jobs: Dict[str, Job]

    def to_dict(self) -> dict:
        return {
            "meta": asdict(self.meta),
            "jobs": {
                job_id: job.__dict__
                for job_id, job in self.jobs.items()
            },
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        meta = SnapshotMeta(**data["meta"])
        jobs = {
            job_id: Job(**job)
            for job_id, job in data["jobs"].items()
        }
        return Snapshot(meta=meta, jobs=jobs)
