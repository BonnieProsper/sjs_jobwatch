from __future__ import annotations

from sjs_sitewatch.alerts.dispatcher import dispatch_alert
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.users.models import AlertSubscription


def run_alert(
    *,
    diff: DiffResult,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    """
    Executes alert logic for a single subscription and diff.
    """
    dispatch_alert(
        diff=diff,
        subscription=subscription,
        dry_run=dry_run,
    )
