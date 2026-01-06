from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from sjs_sitewatch.alerts.dispatcher import dispatch_alert
from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.domain.diff import DiffResult
from sjs_sitewatch.domain.trends import TrendReport
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.alerts.severity import Severity


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _require_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        ) from exc


def send_email_alert(
    *,
    diff: DiffResult,
    to_email: str,
    trends: TrendReport | None = None,
    dry_run: bool = False,
) -> None:
    trends = trends or TrendReport(
        job_counts_by_day={},
        persistent_jobs=[],
        new_jobs=[],
        removed_jobs=[],
        title_changes=[],
        salary_changes=[],
    )

    subscription = AlertSubscription(
        email=to_email,
        ict_only=False,
        region=None,
        min_severity=Severity.LOW,
    )

    changes = dispatch_alert(
        diff=diff,
        trends=trends,
        subscription=subscription,
    )

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
