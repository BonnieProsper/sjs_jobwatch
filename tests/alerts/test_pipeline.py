from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.models import Severity
from sjs_sitewatch.domain.diff import DiffResult, JobChange, FieldChange
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription

from tests.helpers.jobs import make_job


def test_pipeline_scores_and_filters_changes():
    before = make_job(
        id="job-1",
        title="Developer",
        region="Auckland",
        category="ICT",
    )

    after = make_job(
        id="job-1",
        title="Senior Developer",
        region="Auckland",
        category="ICT",
    )

    diff = DiffResult(
        added=[],
        removed=[],
        modified=[
            JobChange(
                job_id="job-1",
                before=before,
                after=after,
                changes=[
                    FieldChange(
                        field="title",
                        before="Developer",
                        after="Senior Developer",
                    )
                ],
            )
        ],
    )

    trends = TrendReport.empty()

    subscription = AlertSubscription(
        email="test@example.com",
        frequency="daily",
        hour=9,
        min_severity=Severity.MEDIUM,
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

    scored = results[0]
    assert scored.change.job_id == "job-1"
    assert scored.severity >= Severity.MEDIUM
