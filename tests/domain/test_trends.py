from datetime import datetime

from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer
from tests.helpers.jobs import make_job


def test_detects_persistent_job():
    snapshot1 = Snapshot(
        captured_at=datetime(2024, 1, 1, 9, 0),
        jobs={
            "1": make_job(id="1", title="Engineer"),
        },
    )

    snapshot2 = Snapshot(
        captured_at=datetime(2024, 1, 2, 9, 0),
        jobs={
            "1": make_job(id="1", title="Engineer"),
        },
    )

    report = TrendAnalyzer([snapshot1, snapshot2]).analyze()

    assert report.persistent_jobs == ["1"]


def test_detects_title_change():
    snapshot1 = Snapshot(
        captured_at=datetime(2024, 1, 1, 9, 0),
        jobs={
            "1": make_job(id="1", title="Junior Dev"),
        },
    )

    snapshot2 = Snapshot(
        captured_at=datetime(2024, 1, 2, 9, 0),
        jobs={
            "1": make_job(id="1", title="Senior Dev"),
        },
    )

    report = TrendAnalyzer([snapshot1, snapshot2]).analyze()

    assert len(report.title_changes) == 1
    change = report.title_changes[0]

    assert change.job_id == "1"
    assert change.before == "Junior Dev"
    assert change.after == "Senior Dev"
