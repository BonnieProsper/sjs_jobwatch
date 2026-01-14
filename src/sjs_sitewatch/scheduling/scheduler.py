from __future__ import annotations

from pathlib import Path
import logging # TODO - use logging.py instead/remove logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from sjs_sitewatch.scheduling.jobs import run_alert_job
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.users.store import SubscriptionStore


logger = logging.getLogger(__name__)


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
        logger.info("Running alerts once for %d subscription(s)", len(subscriptions))
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

    logger.info(
        "Scheduler started with %d subscription(s)",
        len(subscriptions),
    )
    scheduler.start()
