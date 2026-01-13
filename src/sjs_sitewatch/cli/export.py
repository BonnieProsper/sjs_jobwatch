from __future__ import annotations

import click
from pathlib import Path

from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.storage.export import (
    export_jobs_csv,
    export_jobs_json,
)


@click.command()
@click.option(
    "--data-dir",
    type=Path,
    default=Path("data"),
    help="Directory containing snapshot data",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["csv", "json"], case_sensitive=False),
    required=True,
    help="Export format",
)
@click.option(
    "--out",
    type=Path,
    required=True,
    help="Output file path",
)
def export(data_dir: Path, fmt: str, out: Path) -> None:
    """Export jobs from the latest snapshot."""
    store = FilesystemSnapshotStore(data_dir)
    snapshots = store.load_all()

    if not snapshots:
        raise click.ClickException("No snapshots found.")

    jobs = snapshots[-1].jobs.values()

    if fmt == "csv":
        export_jobs_csv(jobs, out)
    else:
        export_jobs_json(jobs, out)

    click.echo(f"Exported {len(list(jobs))} jobs to {out}")
