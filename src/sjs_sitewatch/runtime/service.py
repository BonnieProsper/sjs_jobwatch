from __future__ import annotations

from pathlib import Path

from sjs_sitewatch.scheduling.scheduler import start_scheduler


def run_service(
    *,
    data_dir: Path,
    subscriptions_path: Path,
    dry_run: bool = False,
) -> None:
    """
    Run the long-lived background alerting service.
    """
    start_scheduler(
        data_dir=data_dir,
        subscriptions_path=subscriptions_path,
        dry_run=dry_run,
    )
