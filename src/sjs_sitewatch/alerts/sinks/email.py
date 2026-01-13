from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.sinks.base import AlertSink


SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


def _require_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        ) from exc


class EmailSink(AlertSink):
    """
    Email delivery sink.

    Responsibilities:
    - render scored alert changes
    - deliver via SMTP
    - support dry-run mode

    Assumes changes are already scored and filtered.
    """

    def __init__(
        self,
        *,
        to_email: str,
        dry_run: bool = False,
        smtp_host: str = SMTP_HOST,
        smtp_port: int = SMTP_PORT,
    ) -> None:
        self._to_email = to_email
        self._dry_run = dry_run
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._renderer = AlertRenderer()

    def send(self, changes: Iterable[ScoredChange]) -> None:
        changes = list(changes)
        if not changes:
            return

        msg = EmailMessage()
        msg["To"] = self._to_email
        msg["Subject"] = self._renderer.render_subject(changes)

        msg.set_content(self._renderer.render_text(changes))
        msg.add_alternative(
            self._renderer.render_html(changes),
            subtype="html",
        )

        if self._dry_run:
            print("=== EMAIL (dry run) ===")
            print(msg)
            print("======================")
            return

        sender = _require_env("GMAIL_ADDRESS")
        password = _require_env("GMAIL_APP_PASSWORD")
        msg["From"] = sender

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
        except smtplib.SMTPException as exc:
            raise RuntimeError(
                f"Failed to send alert email to {self._to_email}"
            ) from exc
