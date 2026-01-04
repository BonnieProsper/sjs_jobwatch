from collections import Counter
from datetime import datetime, timezone
from typing import Dict

from sjs_sitewatch.ingestion.normalize import Job
from state.models import Snapshot, SnapshotMeta


def create_snapshot(jobs: Dict[str, Job]) -> Snapshot:
    by_region = Counter(job.region for job in jobs.values() if job.region)

    meta = SnapshotMeta(
        captured_at=datetime.now(tz=timezone.utc).isoformat(),
        total_jobs=len(jobs),
        by_region=dict(by_region),
    )

    return Snapshot(meta=meta, jobs=jobs)
