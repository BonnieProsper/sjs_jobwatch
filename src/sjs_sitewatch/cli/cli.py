from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.alerts.sinks.console import print_alerts
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.users.store import SubscriptionStore
from sjs_sitewatch.cli.export import add_export_subcommand


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sjs-sitewatch",
        description="Track changes in the SJS job market over time",
    )

    subparsers = parser.add_subparsers(dest="command")

    add_export_subcommand(subparsers)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--current", action="store_true")
    parser.add_argument("--summary", action="store_true")

    parser.add_argument("--email", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=Path("subscriptions.json"),
    )

    return parser.parse_args()

    # existing arguments stay exactly as-is



def main() -> None:
    args = parse_args()

    store = FilesystemSnapshotStore(args.data_dir)
    snapshots = store.load_all()

    if not snapshots:
        print("No snapshots found.", file=sys.stderr)
        sys.exit(1)

    if args.current:
        print(f"Current snapshot contains {len(snapshots[-1].jobs)} jobs")
        return

    if len(snapshots) < 2:
        print("Only one snapshot exists — no diffs to show.")
        return

    diff = diff_snapshots(
        snapshots[-2].jobs,
        snapshots[-1].jobs,
    )

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
            send_email_alert(
                diff=diff,
                trends=trends,
                subscription=sub,
                dry_run=args.dry_run,
            )

        return

    # -------------------------
    # Console inspection mode
    # -------------------------
    console_subscription = AlertSubscription(
        email="console",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=console_subscription,
    )

    print_alerts(changes)


if __name__ == "__main__":
    main()


# TODO: merge, new file

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.alerts.sinks.console import ConsoleSink
from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.users.store import SubscriptionStore
from sjs_sitewatch.cli.export import add_export_subcommand


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sjs-sitewatch",
        description="Track changes in the SJS job market over time",
    )

    subparsers = parser.add_subparsers(dest="command")
    add_export_subcommand(subparsers)

    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--current", action="store_true")
    parser.add_argument("--summary", action="store_true")

    parser.add_argument("--email", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=Path("subscriptions.json"),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    store = FilesystemSnapshotStore(args.data_dir)
    snapshots = store.load_all()

    if not snapshots:
        print("No snapshots found.", file=sys.stderr)
        sys.exit(1)

    if args.current:
        print(f"Current snapshot contains {len(snapshots[-1].jobs)} jobs")
        return

    if len(snapshots) < 2:
        print("Only one snapshot exists — no diffs to show.")
        return

    diff = diff_snapshots(
        snapshots[-2].jobs,
        snapshots[-1].jobs,
    )

    trends = TrendAnalyzer(snapshots).analyze()
    pipeline = AlertPipeline()

    # -------------------------
    # Email alert mode
    # -------------------------
    if args.email:
        subs = SubscriptionStore(args.subscriptions).load_all()
        if not subs:
            print("No alert subscriptions found.", file=sys.stderr)
            return

        sink = EmailSink(dry_run=args.dry_run)

        for sub in subs:
            changes = pipeline.run(diff=diff, trends=trends, subscription=sub)
            sink.send(changes, subscription=sub)

        return

    # -------------------------
    # Console inspection mode
    # -------------------------
    console_sub = AlertSubscription(
        email="console",
        ict_only=False,
        region=None,
        frequency="daily",
        hour=0,
        min_severity=Severity.LOW,
    )

    changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=console_sub,
    )

    ConsoleSink().send(changes, subscription=console_sub)


if __name__ == "__main__":
    main()
