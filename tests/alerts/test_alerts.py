from datetime import datetime

from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.snapshot import Snapshot
from sjs_sitewatch.domain.trends import TrendAnalyzer


def _job(job_id: str, title: str) -> Job:
    return Job(
        id=job_id,
        title=title,
        employer="ABC",
        summary=None,
        description=None,
        category="ICT",
        classification=None,
        sub_classification=None,
        job_type="Full Time",
        region="NZ",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=None,
        start_date=None,
        end_date=None,
    )


def test_added_job_is_high_severity():
    change = JobChange(
        job_id="1",
        before=None,
        after=_job("1", "Engineer"),
        changes=[],
    )

    trends = TrendAnalyzer([]).analyze()
    severity = SeverityCalculator().score(change, trends)

    assert severity == Severity.HIGH
