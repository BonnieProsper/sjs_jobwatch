from sjs_sitewatch.domain.diff import FieldChange, JobChange
from sjs_sitewatch.domain.explain import (
    ChangeSeverity,
    explain_field_change,
    explain_changes,
    explain_job_change,
    job_change_severity,
)


def test_explain_added_field():
    change = FieldChange("salary", None, "$100k")

    assert explain_field_change(change) == "salary was added ($100k)"


def test_explain_removed_field():
    change = FieldChange("area", "Auckland", None)

    assert (
        explain_field_change(change)
        == "area was removed (was Auckland)"
    )


def test_explain_changed_field():
    change = FieldChange("title", "Junior", "Senior")

    assert (
        explain_field_change(change)
        == "title changed from Junior to Senior"
    )


def test_explain_multiple_changes():
    changes = [
        FieldChange("salary", None, "$120k"),
        FieldChange("remote", False, True),
    ]

    explanations = explain_changes(changes)

    assert explanations == [
        "salary was added ($120k)",
        "remote changed from False to True",
    ]


def test_explain_job_change():
    job_change = JobChange(
        job_id="1",
        before=None,
        after=None,
        changes=[
            FieldChange("salary", "$100k", "$120k"),
            FieldChange("remote", False, True),
        ],
    )

    explanations = explain_job_change(job_change)

    assert explanations == [
        "salary changed from $100k to $120k",
        "remote changed from False to True",
    ]


def test_job_change_severity_high():
    job_change = JobChange(
        job_id="1",
        before=None,
        after=None,
        changes=[
            FieldChange("title", "Engineer", "Senior Engineer"),
        ],
    )

    assert job_change_severity(job_change) == ChangeSeverity.HIGH


def test_job_change_severity_medium():
    job_change = JobChange(
        job_id="1",
        before=None,
        after=None,
        changes=[
            FieldChange("salary", "$100k", "$120k"),
        ],
    )

    assert job_change_severity(job_change) == ChangeSeverity.MEDIUM


def test_job_change_severity_low():
    job_change = JobChange(
        job_id="1",
        before=None,
        after=None,
        changes=[
            FieldChange("summary", "Old", "New"),
        ],
    )

    assert job_change_severity(job_change) == ChangeSeverity.LOW
