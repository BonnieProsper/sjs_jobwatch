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


# TODO: merge/check file:
from apscheduler.schedulers.blocking import BlockingScheduler
from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.users.store import SubscriptionStore

def run_service():
    scheduler = BlockingScheduler()
    store = SubscriptionStore(...)

    for sub in store.load():
        scheduler.add_job(
            func=run_for_subscription,
            trigger="interval",
            days=1 if sub.cadence == "daily" else 7,
            args=[sub],
        )

    scheduler.start()
