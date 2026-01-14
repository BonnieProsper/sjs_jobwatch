from __future__ import annotations

import click
from pathlib import Path

from sjs_sitewatch.runtime.runner import run_service


@click.command()
@click.option(
    "--data-dir",
    type=Path,
    default=Path("data"),
    help="Directory containing snapshot data",
)
@click.option(
    "--subscriptions",
    type=Path,
    default=Path("subscriptions.json"),
    help="Alert subscriptions file",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Do not send alerts; log instead",
)
@click.option(
    "--once",
    is_flag=True,
    help="Run alerts once and exit (no scheduler)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable debug logging",
)
def run(
    data_dir: Path,
    subscriptions: Path,
    dry_run: bool,
    once: bool,
    verbose: bool,
) -> None:
    """Run the sitewatch alert service."""
    run_service(
        data_dir=data_dir,
        subscriptions_path=subscriptions,
        dry_run=dry_run,
        run_once=once,
        verbose=verbose,
    )
