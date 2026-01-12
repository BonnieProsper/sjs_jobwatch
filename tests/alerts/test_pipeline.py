# TODO: fix
from datetime import date

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


def test_pipeline_filters_by_severity_and_region():
    job_before = Job(
        id="1",
        title="Developer",
        region="Auckland",
        category="ICT",
        pay_min=100000,
        pay_max=120000,
    )

    job_after = Job(
        id="1",
        title="Senior Developer",
        region="Auckland",
        category="ICT",
        pay_min=120000,
        pay_max=140000,
    )

    diff = DiffResult(
        added=[],
        removed=[],
        changed=[
            JobChange(
                job_id="1",
                before=job_before,
                after=job_after,
            )
        ],
    )

    trends = TrendReport.empty()

    subscription = AlertSubscription(
        email="test@example.com",
        frequency="daily",
        hour=9,
        min_severity=3,
        region="Auckland",
        ict_only=True,
    )

    pipeline = AlertPipeline()
    results = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

    assert len(results) == 1
    assert results[0].change.job_id == "1"
    assert results[0].severity >= 3
