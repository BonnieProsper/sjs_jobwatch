from __future__ import annotations

from typing import Iterable, List

from sjs_sitewatch.domain.job import Job
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.explain import (
    explain_job_change,
    job_change_severity,
    ChangeSeverity,
)


def _severity_tag(severity: ChangeSeverity) -> str:
    return {
        ChangeSeverity.HIGH: "[HIGH]",
        ChangeSeverity.MEDIUM: "[MED ]",
        ChangeSeverity.LOW: "[LOW ]",
    }[severity]


# -------------------------
# Job listing presentation
# -------------------------

def print_jobs(jobs: Iterable[Job]) -> None:
    """
    Print a compact table of current jobs.
    """
    rows = []

    for job in jobs:
        rows.append(
            (
                job.id,
                job.title,
                job.employer or "",
                job.region or "",
                job.area or "",
            )
        )

    if not rows:
        print("No jobs found.")
        return

    _print_table(
        headers=["ID", "Title", "Employer", "Region", "Area"],
        rows=rows,
    )


# -------------------------
# Diff presentation
# -------------------------

def print_diff(diff: DiffResult) -> None:
    """
    Print job diffs with severity and explanations.
    """

    if not (diff.added or diff.removed or diff.modified):
        print("No changes detected.")
        return

    for section, changes in (
        ("Added", diff.added),
        ("Removed", diff.removed),
        ("Modified", diff.modified),
    ):
        if not changes:
            continue

        print(f"\n{section} jobs:")
        print("-" * (len(section) + 6))

        for change in changes:
            _print_job_change(change)


def _print_job_change(change: JobChange) -> None:
    severity = job_change_severity(change)
    tag = _severity_tag(severity)

    job = change.after or change.before
    assert job is not None  # for type checkers

    print(f"{tag} {job.title} (ID: {change.job_id})")

    for line in explain_job_change(change):
        print(f"  - {line}")


# -------------------------
# Summary presentation
# -------------------------

def print_summary(diff: DiffResult) -> None:
    """
    Print a one-line summary suitable for cron output.
    """
    print(
        f"Added: {len(diff.added)} | "
        f"Removed: {len(diff.removed)} | "
        f"Modified: {len(diff.modified)}"
    )


# -------------------------
# Internal helpers
# -------------------------

def _print_table(headers: List[str], rows: List[tuple]) -> None:
    """
    Minimal table formatter with aligned columns.
    """
    widths = [
        max(len(str(cell)) for cell in column)
        for column in zip(headers, *rows)
    ]

    def format_row(row):
        return " | ".join(
            str(cell).ljust(width)
            for cell, width in zip(row, widths)
        )

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))

    for row in rows:
        print(format_row(row))
