from __future__ import annotations

import argparse
from pathlib import Path

from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.storage.export import (
    export_jobs_csv,
    export_jobs_json,
)


def add_export_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "export",
        help="Export jobs from the latest snapshot",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing snapshot data",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        required=True,
        help="Export format",
    )

    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output file path",
    )

    parser.set_defaults(func=_run_export)


def _run_export(args: argparse.Namespace) -> None:
    store = FilesystemSnapshotStore(args.data_dir)
    snapshots = store.load_all()

    if not snapshots:
        raise SystemExit("No snapshots found.")

    jobs = snapshots[-1].jobs

    if args.format == "csv":
        export_jobs_csv(jobs, args.out)
    else:
        export_jobs_json(jobs, args.out)

    print(f"Exported {len(jobs)} jobs to {args.out}")
