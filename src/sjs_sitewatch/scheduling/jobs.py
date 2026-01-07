from __future__ import annotations

from sjs_sitewatch.alerts.dispatcher import AlertDispatcher
from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.trends import TrendAnalyzer
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
    trends = TrendAnalyzer(snapshots).analyze()

    dispatcher = AlertDispatcher()

    scored_changes = dispatcher.dispatch(
        diff=diff,
        trends=trends,
    )

    filtered_changes = dispatcher.filter_min_severity(
        scored_changes,
        subscription.min_severity,
    )

    if not filtered_changes:
        return

    send_email_alert(
        filtered_changes,
        to_email=subscription.email,
        dry_run=dry_run,
    )
