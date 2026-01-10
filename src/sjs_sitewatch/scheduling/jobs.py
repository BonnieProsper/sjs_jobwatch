from __future__ import annotations

from pathlib import Path

from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.users.models import AlertSubscription


def run_alert_job(
    *,
    data_dir: Path,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    """
    Execute a single alert run for one subscription.

    Responsibilities:
    - load stored snapshots
    - compute diff + trends
    - delegate alert decision + delivery
    """
    store = FilesystemSnapshotStore(data_dir)
    snapshots = store.load_all()

    # Need at least two snapshots to compute a diff
    if len(snapshots) < 2:
        return

    previous, current = snapshots[-2], snapshots[-1]

    diff = diff_snapshots(previous.jobs, current.jobs)
    trends = TrendAnalyzer(snapshots).analyze()

    send_email_alert(
        diff=diff,
        trends=trends,
        subscription=subscription,
        dry_run=dry_run,
    )
