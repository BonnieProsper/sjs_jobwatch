from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.domain.diff import DiffResult, diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.users.store import SubscriptionStore
from sjs_sitewatch.alerts.email import send_email_alert


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
        help="Directory containing snapshot data",
    )

    parser.add_argument("--current", action="store_true")
    parser.add_argument("--summary", action="store_true")

    parser.add_argument(
        "--email",
        action="store_true",
        help="Dispatch alerts using registered subscriptions",
    )

    parser.add_argument("--dry-run", action="store_true")

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

def present_summary(diff: DiffResult) -> None:
    print(
        f"Added: {len(diff.added)} | "
        f"Removed: {len(diff.removed)} | "
        f"Changed: {len(diff.modified)}"
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

    diff = diff_snapshots(
        snapshots[-2].jobs,
        snapshots[-1].jobs,
    )

    if args.summary:
        present_summary(diff)
        return

    trends = TrendAnalyzer(snapshots).analyze()
    pipeline = AlertPipeline()

    # -------------------------
    # Email dispatch mode
    # -------------------------

    if args.email:
        subs = SubscriptionStore(args.subscriptions).load_all()

        if not subs:
            print("No alert subscriptions found.", file=sys.stderr)
            return

        for sub in subs:
            changes = pipeline.run(
                diff=diff,
                trends=trends,
                subscription=sub,
            )

            if not changes:
                continue

            send_email_alert(
                diff=diff,
                trends=trends,
                to_email=sub.email,
                dry_run=args.dry_run,
            )

        return

    # -------------------------
    # Default: console inspection
    # -------------------------

    from sjs_sitewatch.alerts.renderer import AlertRenderer
    from sjs_sitewatch.users.models import AlertSubscription
    from sjs_sitewatch.alerts.severity import Severity

    # Console inspection intentionally bypasses filtering
    console_subscription = AlertSubscription(
        email="console",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    alerts = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=console_subscription,
    )

    if not alerts:
        print("No significant changes detected.")
        return

    renderer = AlertRenderer()
    print(renderer.render_text(alerts))


if __name__ == "__main__":
    main()
