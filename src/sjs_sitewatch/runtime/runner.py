from __future__ import annotations

from pathlib import Path
import logging

from sjs_sitewatch.logging import configure_logging
from sjs_sitewatch.scheduling.scheduler import start_scheduler

log = logging.getLogger(__name__)


def run_service(
    *,
    data_dir: Path,
    subscriptions_path: Path,
    dry_run: bool = False,
    run_once: bool = False,
    verbose: bool = False,
) -> None:
    """
    Run the long-lived background alerting service
    or execute a single evaluation pass.
    """
    configure_logging(verbose=verbose)

    log.info(
        "Starting sitewatch service (run_once=%s, dry_run=%s)",
        run_once,
        dry_run,
    )

    start_scheduler(
        data_dir=data_dir,
        subscriptions_path=subscriptions_path,
        dry_run=dry_run,
        run_once=run_once,
    )
