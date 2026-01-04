from collections import Counter
from typing import Iterable, Dict, Tuple
from datetime import date

from sjs_sitewatch.ingestion.normalize import Job
from sjs_sitewatch.alerts.filters import is_ict_job
from sjs_sitewatch.domain.diff import JobChange
from state.models import Snapshot


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def summarize_jobs(jobs: Iterable[Job]) -> str:
    if not jobs:
        return "None"

    by_region = Counter(job.region for job in jobs if job.region)
    return ", ".join(
        f"{count} in {region}"
        for region, count in sorted(by_region.items())
    )


# ─────────────────────────────────────────────
# Change reports
# ─────────────────────────────────────────────

def report_added_jobs(jobs: list[Job]) -> None:
    print("\n🆕 New jobs:")
    print(f"  Total: {len(jobs)}")
    print(f"  By region: {summarize_jobs(jobs)}")


def report_removed_jobs(jobs: list[Job]) -> None:
    print("\n❌ Removed jobs:")
    print(f"  Total: {len(jobs)}")
    print(f"  By region: {summarize_jobs(jobs)}")


def report_ict_added_jobs(jobs: list[Job]) -> None:
    ict_jobs = [job for job in jobs if is_ict_job(job)]

    print("\n💻 New ICT jobs:")
    print(f"  Total: {len(ict_jobs)}")

    if ict_jobs:
        print(f"  By region: {summarize_jobs(ict_jobs)}")


def report_updated_jobs(
    updated: Dict[str, Tuple[Job, Job, list[JobChange]]],
    severity: str | None = None,
) -> None:
    print("\n✏️ Updated jobs:")

    if not updated:
        print("  None")
        return

    for _, (_, job, changes) in updated.items():
        if severity:
            changes = [
                c for c in changes
                if c.severity == severity.upper()
            ]

        if not changes:
            continue

        print(f"- {job.title} ({job.region})")

        for change in changes:
            old = change.old or "—"
            new = change.new or "—"
            print(f"  • {change.field}: {old} → {new}")


# ─────────────────────────────────────────────
# Snapshot reporting
# ─────────────────────────────────────────────

def print_current_snapshot(
    snapshot: Snapshot,
    summary_only: bool = False,
) -> None:
    meta = snapshot.meta

    print("\n📸 Current snapshot")
    print(f"Captured: {meta.captured_at}")
    print(f"Total jobs: {meta.total_jobs}")

    print("\nBy region:")
    for region, count in sorted(meta.by_region.items()):
        print(f"  {region}: {count}")

    if summary_only:
        return

    print("\nSample listings:")
    for job in list(snapshot.jobs.values())[:5]:
        print(f"- {job.title} ({job.region})")


# ─────────────────────────────────────────────
# High-level summary
# ─────────────────────────────────────────────

def report_summary(diff) -> None:
    print(f"\n📊 SJS Job Watch — {date.today().isoformat()}\n")
    print(f"+ {len(diff.added)} new jobs")
    print(f"- {len(diff.removed)} removed")
    print(f"~ {len(diff.updated)} updated\n")

    regions = Counter(job.region for job in diff.added if job.region)
    if regions:
        print("Regions:")
        for region, count in sorted(regions.items()):
            print(f"  {region}: +{count}")
