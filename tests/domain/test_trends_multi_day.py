from datetime import datetime, timedelta

from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer
from tests.helpers.jobs import make_job


def snapshot_at(day_offset: int, jobs):
    return Snapshot(
        jobs={job.id: job for job in jobs},
        captured_at=datetime(2025, 1, 1) + timedelta(days=day_offset),
    )


def test_job_removed_then_readded_counts_as_removed_and_new():
    """
    A job that disappears and later reappears should be counted as:
    - removed (on disappearance)
    - new (on reappearance)
    and should NOT be considered persistent.
    """
    snapshots = [
        snapshot_at(0, [make_job(id="job-1")]),
        snapshot_at(1, []),
        snapshot_at(2, [make_job(id="job-1")]),
    ]

    report = TrendAnalyzer(snapshots).analyze()

    assert report.persistent_jobs == []
    assert report.new_jobs == ["job-1"]
    assert report.removed_jobs == ["job-1"]
