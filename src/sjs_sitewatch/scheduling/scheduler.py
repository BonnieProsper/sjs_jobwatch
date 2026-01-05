from __future__ import annotations

from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from sjs_sitewatch.scheduling.jobs import run_alert_job
from sjs_sitewatch.users.store import SubscriptionStore
from sjs_sitewatch.users.models import AlertSubscription


def _job_id(sub: AlertSubscription) -> str:
    """
    Stable scheduler job ID per subscription.
    """
    return f"{sub.email}:{sub.frequency}:{sub.hour}"


def start_scheduler(
    *,
    data_dir: Path,
    subscriptions_path: Path,
    dry_run: bool = False,
) -> None:
    scheduler = BlockingScheduler()
    store = SubscriptionStore(subscriptions_path)

    subscriptions = store.load_all()

    for sub in subscriptions:
        sub.validate()

        scheduler.add_job(
            run_alert_job,
            trigger="cron",
            id=_job_id(sub),
            hour=sub.hour,
            minute=0,
            replace_existing=True,
            kwargs={
                "data_dir": data_dir,
                "subscription": sub,
                "dry_run": dry_run,
            },
        )

    print(
        f"Scheduler started with {len(subscriptions)} subscription(s)"
    )
    scheduler.start()
