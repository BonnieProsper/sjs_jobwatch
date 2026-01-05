from datetime import datetime, timedelta

from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer
from tests.helpers.jobs import make_job


def snapshot_at(day_offset: int, jobs):
    return Snapshot(
        jobs={job.id: job for job in jobs},
        captured_at=datetime(2025, 1, 1) + timedelta(days=day_offset),
    )


def test_persistent_job_detection():
    snapshots = [
        snapshot_at(0, [make_job(id="job-1")]),
        snapshot_at(1, [make_job(id="job-1")]),
        snapshot_at(2, [make_job(id="job-1")]),
    ]

    report = TrendAnalyzer(snapshots).analyze()

    assert report.persistent_jobs == ["job-1"]
    assert report.new_jobs == []
    assert report.removed_jobs == []


def test_new_and_removed_jobs():
    snapshots = [
        snapshot_at(0, [make_job(id="job-1")]),
        snapshot_at(1, [make_job(id="job-1"), make_job(id="job-2")]),
    ]

    report = TrendAnalyzer(snapshots).analyze()

    assert report.new_jobs == ["job-2"]
    assert report.removed_jobs == []
    assert report.persistent_jobs == ["job-1"]


def test_removed_job_detection():
    snapshots = [
        snapshot_at(0, [make_job(id="job-1"), make_job(id="job-2")]),
        snapshot_at(1, [make_job(id="job-1")]),
    ]

    report = TrendAnalyzer(snapshots).analyze()

    assert report.removed_jobs == ["job-2"]
    assert report.new_jobs == []
    assert report.persistent_jobs == ["job-1"]


def test_title_and_salary_changes():
    snapshots = [
        snapshot_at(0, [make_job(id="job-1", title="Engineer", pay_min=100)]),
        snapshot_at(1, [make_job(id="job-1", title="Senior Engineer", pay_min=120)]),
    ]

    report = TrendAnalyzer(snapshots).analyze()

    assert len(report.title_changes) == 1
    assert len(report.salary_changes) == 1


def test_empty_snapshots():
    report = TrendAnalyzer([]).analyze()

    assert report.job_counts_by_day == {}
    assert report.persistent_jobs == []
    assert report.new_jobs == []
    assert report.removed_jobs == []
