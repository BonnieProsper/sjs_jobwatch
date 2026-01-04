from __future__ import annotations

from sjs_sitewatch.alerts.dispatcher import dispatch_alert
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.storage.filesystem import FilesystemSnapshotStore
from sjs_sitewatch.users.models import AlertSubscription


def run_alert_job(
    *,
    data_dir,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    store = FilesystemSnapshotStore(data_dir)
    snapshots = store.load_all()

    if len(snapshots) < 2:
        return

    previous, current = snapshots[-2], snapshots[-1]
    diff = diff_snapshots(previous.jobs, current.jobs)

    dispatch_alert(
        diff=diff,
        subscription=subscription,
        dry_run=dry_run,
    )
