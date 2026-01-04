from datetime import datetime

from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer
from tests.helpers.jobs import make_job


def test_salary_change_is_high_severity():
    snapshot1 = Snapshot(
        captured_at=datetime(2024, 1, 1, 9, 0),
        jobs={
            "1": make_job(id="1", pay_min=100000, pay_max=120000),
        },
    )

    snapshot2 = Snapshot(
        captured_at=datetime(2024, 1, 2, 9, 0),
        jobs={
            "1": make_job(id="1", pay_min=110000, pay_max=130000),
        },
    )

    trends = TrendAnalyzer([snapshot1, snapshot2]).analyze()

    change = JobChange(
        job_id="1",
        before=snapshot1.jobs["1"],
        after=snapshot2.jobs["1"],
        changes=[],
    )

    severity = SeverityCalculator().score(change, trends)

    assert severity == Severity.HIGH
