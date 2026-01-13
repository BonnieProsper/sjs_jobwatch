from __future__ import annotations

from pathlib import Path

from sjs_sitewatch.scheduling.scheduler import start_scheduler


def run_service(
    *,
    data_dir: Path,
    subscriptions_path: Path,
    dry_run: bool = False,
    run_once: bool = False,
) -> None:
    """
    Run the long-lived background alerting service 
    or execute a single evaluation pass.

    This function blocks the process and periodically:
    - loads snapshots
    - computes diffs + trends
    - evaluates subscriptions
    - sends email alerts
    """
    start_scheduler(
        data_dir=data_dir,
        subscriptions_path=subscriptions_path,
        dry_run=dry_run,
        run_once=run_once,
    )
