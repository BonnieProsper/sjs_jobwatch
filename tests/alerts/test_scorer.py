from sjs_sitewatch.alerts.scorer import AlertScorer
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import DiffResult, JobChange, FieldChange
from sjs_sitewatch.domain.trends import TrendReport

from tests.helpers.jobs import make_job


def empty_trends() -> TrendReport:
    return TrendReport(
        job_counts_by_day={},
        persistent_jobs=[],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[],
        salary_changes=[],
    )


def test_scorer_scores_modified_job() -> None:
    before = make_job(
        id="job-1",
        title="Junior Developer",
    )
    after = make_job(
        id="job-1",
        title="Senior Developer",
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
                        before="Junior Developer",
                        after="Senior Developer",
                    )
                ],
            )
        ],
    )

    scorer = AlertScorer()
    scored = scorer.score_all(
        diff=diff,
        trends=empty_trends(),
    )

    assert len(scored) == 1

    change = scored[0]
    assert change.change.job_id == "job-1"
    assert change.severity in {
        Severity.LOW,
        Severity.MEDIUM,
        Severity.HIGH,
    }
    assert change.reason
