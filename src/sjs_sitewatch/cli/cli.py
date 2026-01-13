from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sjs_sitewatch.cli.export import add_export_subcommand
from sjs_sitewatch.scheduling.scheduler import start_scheduler
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sjs-sitewatch",
        description="Track changes in the SJS job market over time",
    )

    subparsers = parser.add_subparsers(dest="command")
    add_export_subcommand(subparsers)

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing snapshot data",
    )

    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=Path("subscriptions.json"),
        help="Alert subscriptions file",
    )

    parser.add_argument(
        "--current",
        action="store_true",
        help="Show job count for the latest snapshot",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send emails; print instead",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run alerts once and exit (no scheduler)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # -------------------------
    # Subcommands (e.g. export)
    # -------------------------
    if hasattr(args, "func"):
        args.func(args)
        return

    # -------------------------
    # Snapshot inspection mode
    # -------------------------
    store = FilesystemSnapshotStore(args.data_dir)
    snapshots = store.load_all()

    if not snapshots:
        print("No snapshots found.", file=sys.stderr)
        sys.exit(1)

    if args.current:
        print(f"Current snapshot contains {len(snapshots[-1].jobs)} jobs")
        return

    # -------------------------
    # Alert execution mode
    # -------------------------
    start_scheduler(
        data_dir=args.data_dir,
        subscriptions_path=args.subscriptions,
        dry_run=args.dry_run,
        run_once=args.once,
    )


if __name__ == "__main__":
    main()
