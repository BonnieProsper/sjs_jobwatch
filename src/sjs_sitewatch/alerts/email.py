from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.renderer import AlertRenderer


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
    changes: list[ScoredChange],
    *,
    to_email: str,
    dry_run: bool = False,
) -> None:
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
