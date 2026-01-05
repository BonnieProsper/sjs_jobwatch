from datetime import datetime

from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer

from tests.helpers.jobs import make_job


def test_title_change_on_persistent_job_is_high_severity():
    snapshots = [
        Snapshot(
            captured_at=datetime(2024, 1, 1),
            jobs={"1": make_job(id="1", title="Engineer")},
        ),
        Snapshot(
            captured_at=datetime(2024, 1, 2),
            jobs={"1": make_job(id="1", title="Senior Engineer")},
        ),
    ]

    trends = TrendAnalyzer(snapshots).analyze()

    change = JobChange(
        job_id="1",
        before=make_job(id="1", title="Engineer"),
        after=make_job(id="1", title="Senior Engineer"),
        changes=[],
    )

    severity = SeverityCalculator().score(change, trends)

    assert severity == Severity.HIGH


def test_new_job_is_high_severity():
    trends = TrendAnalyzer([]).analyze()

    change = JobChange(
        job_id="1",
        before=None,
        after=make_job(id="1"),
        changes=[],
    )

    severity = SeverityCalculator().score(change, trends)

    assert severity == Severity.HIGH


def test_removed_job_is_medium_severity():
    trends = TrendAnalyzer([]).analyze()

    change = JobChange(
        job_id="1",
        before=make_job(id="1"),
        after=None,
        changes=[],
    )

    severity = SeverityCalculator().score(change, trends)

    assert severity == Severity.MEDIUM
