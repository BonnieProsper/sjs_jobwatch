from enum import IntEnum
from typing import Iterable, List

from .diff import FieldChange, JobChange


class ChangeSeverity(IntEnum):
    """
    Domain-level severity for a job change.

    Ordered intentionally so comparisons like:
        severity >= ChangeSeverity.MEDIUM
    are meaningful and type-safe.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# Severity classification
HIGH_IMPACT_FIELDS = {
    "title",
    "category",
    "job_type",
    "employer",
}

MEDIUM_IMPACT_FIELDS = {
    # canonical job fields
    "pay_min",
    "pay_max",
    "region",
    "area",

    # semantic / human-facing aliases
    "salary",
}

LOW_IMPACT_FIELDS = {
    "summary",
    "description",
    "classification",
    "sub_classification",
}


def classify_severity(field: str) -> ChangeSeverity:
    """
    Classify severity of a field change.

    Note:
    Some fields (e.g. 'salary') are semantic aliases used in explanations
    and diffs, even if the underlying Job model stores them differently.
    """
    if field in HIGH_IMPACT_FIELDS:
        return ChangeSeverity.HIGH

    if field in MEDIUM_IMPACT_FIELDS:
        return ChangeSeverity.MEDIUM

    return ChangeSeverity.LOW


# Explanation helpers
def explain_field_change(change: FieldChange) -> str:
    field = change.field

    if change.before is None and change.after is not None:
        return f"{field} was added ({change.after})"

    if change.before is not None and change.after is None:
        return f"{field} was removed (was {change.before})"

    return f"{field} changed from {change.before} to {change.after}"


def explain_changes(changes: Iterable[FieldChange]) -> List[str]:
    return [explain_field_change(change) for change in changes]


def explain_job_change(job_change: JobChange) -> List[str]:
    return explain_changes(job_change.changes)


# Severity aggregation
def job_change_severity(job_change: JobChange) -> ChangeSeverity:
    """
    Determine the overall severity of a job change based on the most
    impactful field that changed.
    """
    if not job_change.changes:
        return ChangeSeverity.LOW

    severities = {
        classify_severity(change.field)
        for change in job_change.changes
    }

    return max(severities)
