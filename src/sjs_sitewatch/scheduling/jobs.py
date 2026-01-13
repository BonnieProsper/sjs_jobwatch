from __future__ import annotations

from pathlib import Path

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.sinks.email import EmailSink
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
    Execute one scheduled alert evaluation for a single subscription.
    """
    store = FilesystemSnapshotStore(data_dir)
    snapshots = store.load_all()

    if len(snapshots) < 2:
        return

    previous, current = snapshots[-2], snapshots[-1]

    diff = diff_snapshots(previous.jobs, current.jobs)
    trends = TrendAnalyzer(snapshots).analyze()

    pipeline = AlertPipeline()
    scored_changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

    sink = EmailSink(
        to_email=subscription.email,
        dry_run=dry_run,
    )

    sink.send(scored_changes)
