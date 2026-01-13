from __future__ import annotations

from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from sjs_sitewatch.scheduling.jobs import run_alert_job
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.users.store import SubscriptionStore


def _job_id(sub: AlertSubscription) -> str:
    return f"alert:{sub.email}:{sub.frequency}:{sub.hour}"


def start_scheduler(
    *,
    data_dir: Path,
    subscriptions_path: Path,
    dry_run: bool = False,
    run_once: bool = False,
) -> None:
    store = SubscriptionStore(subscriptions_path)
    subscriptions = store.load_all()

    # -------------------------
    # Once mode (no scheduler)
    # -------------------------
    if run_once:
        for sub in subscriptions:
            sub.validate()
            run_alert_job(
                data_dir=data_dir,
                subscription=sub,
                dry_run=dry_run,
            )
        return

    # -------------------------
    # Scheduled mode
    # -------------------------
    scheduler = BlockingScheduler(timezone="UTC")

    for sub in subscriptions:
        sub.validate()

        if sub.frequency == "weekly":
            trigger = CronTrigger(
                day_of_week="mon",
                hour=sub.hour,
                minute=0,
            )
        else:
            trigger = CronTrigger(
                hour=sub.hour,
                minute=0,
            )

        scheduler.add_job(
            run_alert_job,
            trigger=trigger,
            id=_job_id(sub),
            replace_existing=True,
            kwargs={
                "data_dir": data_dir,
                "subscription": sub,
                "dry_run": dry_run,
            },
        )

    print(f"Scheduler started with {len(subscriptions)} subscription(s)")
    scheduler.start()
