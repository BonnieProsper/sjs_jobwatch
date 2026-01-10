from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from sjs_sitewatch.alerts.pipeline import AlertPipeline
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _require_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        ) from exc


# =====================================================
# Public API (used by scheduler / tests)
# =====================================================

def send_email_alert(
    *,
    diff: DiffResult,
    trends: TrendReport,
    subscription: AlertSubscription,
    dry_run: bool = False,
) -> None:
    """
    Run the alert pipeline and send an email if changes exist.
    """
    pipeline = AlertPipeline()

    changes = pipeline.run(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

    _send_email_from_changes(
        changes,
        to_email=subscription.email,
        dry_run=dry_run,
    )


# =====================================================
# Core email sender (pure, reusable)
# =====================================================

def _send_email_from_changes(
    changes: Iterable[ScoredChange],
    *,
    to_email: str,
    dry_run: bool = False,
) -> None:
    changes = list(changes)
    if not changes:
        return

    renderer = AlertRenderer()

    msg = EmailMessage()
    msg["Subject"] = renderer.render_subject(changes)
    msg["To"] = to_email

    msg.set_content(renderer.render_text(changes))
    msg.add_alternative(
        renderer.render_html(changes),
        subtype="html",
    )

    if dry_run:
        print("=== EMAIL (dry run) ===")
        print(msg)
        print("======================")
        return

    sender = _require_env("GMAIL_ADDRESS")
    password = _require_env("GMAIL_APP_PASSWORD")
    msg["From"] = sender

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
