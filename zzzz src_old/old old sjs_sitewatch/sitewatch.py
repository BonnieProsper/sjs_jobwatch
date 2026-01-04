import asyncio
from collections import Counter
from datetime import datetime, timezone

from ingestion.capture import capture_jobs
from sjs_sitewatch.ingestion.normalize import normalize_jobs
from sjs_sitewatch.domain.diff import diff_jobs
from sjs_sitewatch.report import (
    report_added_jobs,
    report_removed_jobs,
    report_ict_added_jobs,
    report_updated_jobs,
    print_current_snapshot,
)
from sjs_sitewatch.cli.cli import parse_args
from sjs_sitewatch.alerts.filters import filter_ict, filter_region
from state.store import load_latest_snapshot, save_snapshot
from state.models import Snapshot, SnapshotMeta
from sjs_sitewatch.alerts import select_alerts
from sjs_sitewatch.alerts_email import send_daily_ict_summary


def build_snapshot(jobs: dict) -> Snapshot:
    """
    Build an immutable Snapshot + SnapshotMeta.
    """
    by_region = Counter(
        job.region for job in jobs.values() if job.region
    )

    meta = SnapshotMeta(
        captured_at=datetime.now(timezone.utc).isoformat(),
        total_jobs=len(jobs),
        by_region=dict(by_region),
    )

    return Snapshot(
        meta=meta,
        jobs=jobs,
    )


async def main() -> None:
    args = parse_args()

    # ─────────────────────────────────────
    # Ingest + normalize
    # ─────────────────────────────────────
    raw_jobs = await capture_jobs()
    normalized = normalize_jobs(raw_jobs)

    current_jobs = {job.job_id: job for job in normalized}
    snapshot = build_snapshot(current_jobs)

    previous_snapshot = load_latest_snapshot()
    previous_jobs = previous_snapshot.jobs if previous_snapshot else {}

    # ─────────────────────────────────────
    # Snapshot-only mode
    # ─────────────────────────────────────
    if args.current:
        jobs = list(current_jobs.values())

        if args.region:
            jobs = filter_region(jobs, args.region)

        if args.ict_only:
            jobs = filter_ict(jobs)

        # Create a filtered snapshot ONLY for reporting
        filtered_snapshot = Snapshot(
            meta=snapshot.meta,
            jobs={job.job_id: job for job in jobs},
        )

        print_current_snapshot(
            filtered_snapshot,
            summary_only=args.summary_only,
        )

        save_snapshot(snapshot)
        return

    # ─────────────────────────────────────
    # Diff mode
    # ─────────────────────────────────────
    diff = diff_jobs(previous_jobs, current_jobs)

    added = diff.added
    removed = diff.removed
    updated = diff.updated

    # Apply presentation filters
    if args.region:
        added = filter_region(added, args.region)
        removed = filter_region(removed, args.region)
        updated = {
            job_id: change
            for job_id, change in updated.items()
            if change[1].region.lower() == args.region.lower()
        }

    if args.ict_only:
        added = filter_ict(added)

    if args.watch_region:
        payload = select_alerts(
            diff,
            region=args.watch_region,
            severity=args.severity,
        )

        if payload["added"] or payload["updated"]:
            send_daily_ict_summary(diff)

    # ─────────────────────────────────────
    # Reporting
    # ─────────────────────────────────────
    print("\n📊 Job market snapshot")
    print(f"Total jobs tracked: {snapshot.meta.total_jobs}")

    report_added_jobs(added)
    report_removed_jobs(removed)
    report_updated_jobs(updated, severity=args.severity)

    report_ict_added_jobs(
        added if args.ict_only else diff.added
    )

    save_snapshot(snapshot)


if __name__ == "__main__":
    asyncio.run(main())
