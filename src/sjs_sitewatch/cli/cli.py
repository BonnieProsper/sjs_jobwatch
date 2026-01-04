from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sjs_sitewatch.domain.diff import DiffResult, JobChange, diff_snapshots
from sjs_sitewatch.domain.explain import explain_job_change, job_change_severity
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.alerts.filters import is_ict_job
from sjs_sitewatch.alerts.dispatcher import dispatch
from sjs_sitewatch.users.store import SubscriptionStore


# -------------------------
# CLI argument parsing
# -------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sjs-sitewatch",
        description="Track changes in the SJS job market over time",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing snapshot data (default: ./data)",
    )

    parser.add_argument("--current", action="store_true")
    parser.add_argument("--summary", action="store_true")

    parser.add_argument(
        "--email",
        action="store_true",
        help="Dispatch alerts using registered subscriptions",
    )

    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ict-only", action="store_true")
    parser.add_argument("--region")

    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=Path("subscriptions.json"),
        help="Path to alert subscriptions file",
    )

    return parser.parse_args()


# -------------------------
# Presentation helpers
# -------------------------

def present_job_change(change: JobChange) -> None:
    job = change.after or change.before
    assert job is not None

    severity = job_change_severity(change)
    explanations = explain_job_change(change)

    print(f"[{severity.name}] {job.title} (ID: {job.id})")

    for line in explanations:
        print(f"  - {line}")

    print()


def present_diff(diff: DiffResult) -> None:
    for c in diff.added + diff.removed + diff.modified:
        present_job_change(c)


def present_summary(diff: DiffResult) -> None:
    print(
        f"Added: {len(diff.added)} | "
        f"Removed: {len(diff.removed)} | "
        f"Changed: {len(diff.modified)}"
    )


# -------------------------
# Filtering
# -------------------------

def filter_diff(
    diff: DiffResult,
    *,
    ict_only: bool,
    region: str | None,
) -> DiffResult:
    def matches(change: JobChange) -> bool:
        job = change.after or change.before
        if job is None:
            return False

        if ict_only and not is_ict_job(job):
            return False

        if region and job.region and job.region.lower() != region.lower():
            return False

        return True

    return DiffResult(
        added=[c for c in diff.added if matches(c)],
        removed=[c for c in diff.removed if matches(c)],
        modified=[c for c in diff.modified if matches(c)],
    )


# -------------------------
# Main entry point
# -------------------------

def main() -> None:
    args = parse_args()

    store = FilesystemSnapshotStore(args.data_dir)
    snapshots = store.load_all()

    if not snapshots:
        print("No snapshots found. Run ingestion first.", file=sys.stderr)
        sys.exit(1)

    if args.current:
        print(f"Current snapshot contains {len(snapshots[-1].jobs)} jobs")
        return

    if len(snapshots) < 2:
        print("Only one snapshot exists — no diffs to show.", file=sys.stderr)
        return

    diff = diff_snapshots(snapshots[-2].jobs, snapshots[-1].jobs)

    diff = filter_diff(
        diff,
        ict_only=args.ict_only,
        region=args.region,
    )

    if args.email:
        store = SubscriptionStore(args.subscriptions)
        for sub in store.load_all():
            dispatch(
                diff=diff,
                subscription=sub,
                dry_run=args.dry_run,
            )
        return

    if args.summary:
        present_summary(diff)
        return

    present_diff(diff)


if __name__ == "__main__":
    main()
