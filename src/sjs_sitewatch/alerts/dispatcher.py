from __future__ import annotations

from typing import List

from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.alerts.filters import filter_ict
from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.domain.explain import job_change_severity, ChangeSeverity
from sjs_sitewatch.users.models import AlertSubscription


def _filter_changes(
    diff: DiffResult,
    subscription: AlertSubscription,
) -> List[JobChange]:
    """
    Apply subscription-level filters to a diff.
    """
    changes = diff.added + diff.modified

    if subscription.ict_only:
        changes = [
            c for c in changes
            if c.after and filter_ict([c.after])
        ]

    if subscription.region:
        changes = [
            c for c in changes
            if c.after and c.after.region == subscription.region
        ]

    return changes


def dispatch_alert(
    *,
    diff: DiffResult,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    """
    Decide whether an alert should be sent and dispatch it.
    """
    relevant = _filter_changes(diff, subscription)

    if not relevant:
        return

    # Domain-driven severity gate
    high_signal = [
        c for c in relevant
        if job_change_severity(c) >= ChangeSeverity.MEDIUM
    ]

    if not high_signal:
        return

    send_email_alert(
        diff=DiffResult(
            added=[c for c in high_signal if c.before is None],
            removed=[],
            modified=[c for c in high_signal if c.before is not None],
        ),
        to_email=subscription.email,
        dry_run=dry_run,
    )
