from datetime import date

from sjs_sitewatch.alerts.severity import Severity, SeverityCalculator
from sjs_sitewatch.domain.diff import JobChange
from sjs_sitewatch.domain.trends import SalaryChange, TitleChange, TrendReport
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


def test_added_job_is_high_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=None,
        after=make_job(id="job-1"),
        changes=[],
    )

    severity = calc.score(change, empty_trends())

    assert severity == Severity.HIGH


def test_removed_job_is_medium_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=make_job(id="job-1"),
        after=None,
        changes=[],
    )

    severity = calc.score(change, empty_trends())

    assert severity == Severity.MEDIUM


def test_salary_change_is_high_severity() -> None:
    calc = SeverityCalculator()

    before = make_job(id="job-1", pay_min=90000)
    after = make_job(id="job-1", pay_min=110000)

    change = JobChange(
        job_id="job-1",
        before=before,
        after=after,
        changes=[],
    )

    trends = TrendReport(
        job_counts_by_day={},
        persistent_jobs=[],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[],
        salary_changes=[
            SalaryChange(
                job_id="job-1",
                before_min=90000,
                after_min=110000,
                before_max=120000,
                after_max=120000,
                day=date.today(),
            )
        ],
    )

    severity = calc.score(change, trends)

    assert severity == Severity.HIGH


def test_title_change_persistent_job_is_high_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=make_job(id="job-1", title="Engineer"),
        after=make_job(id="job-1", title="Senior Engineer"),
        changes=[],
    )

    trends = TrendReport(
        job_counts_by_day={},
        persistent_jobs=["job-1"],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[
            TitleChange(
                job_id="job-1",
                before="Engineer",
                after="Senior Engineer",
                day=date.today(),
            )
        ],
        salary_changes=[],
    )

    severity = calc.score(change, trends)

    assert severity == Severity.HIGH


def test_title_change_non_persistent_job_is_medium_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=make_job(id="job-1", title="Engineer"),
        after=make_job(id="job-1", title="Engineer II"),
        changes=[],
    )

    trends = TrendReport(
        job_counts_by_day={},
        persistent_jobs=[],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[
            TitleChange(
                job_id="job-1",
                before="Engineer",
                after="Engineer II",
                day=date.today(),
            )
        ],
        salary_changes=[],
    )

    severity = calc.score(change, trends)

    assert severity == Severity.MEDIUM


def test_persistent_job_with_other_change_is_medium_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=make_job(id="job-1"),
        after=make_job(id="job-1"),
        changes=[],
    )

    trends = TrendReport(
        job_counts_by_day={},
        persistent_jobs=["job-1"],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[],
        salary_changes=[],
    )

    severity = calc.score(change, trends)

    assert severity == Severity.MEDIUM


def test_unremarkable_change_is_low_severity() -> None:
    calc = SeverityCalculator()

    change = JobChange(
        job_id="job-1",
        before=make_job(id="job-1"),
        after=make_job(id="job-1"),
        changes=[],
    )

    severity = calc.score(change, empty_trends())

    assert severity == Severity.LOW
