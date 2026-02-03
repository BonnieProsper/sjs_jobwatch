from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Iterable
from xmlrpc import server

from sjs_sitewatch import config
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.sinks.base import AlertSink

log = logging.getLogger(__name__)


class EmailSink(AlertSink):
    """
    Email delivery sink.

    Responsibilities:
    - render alert content
    - deliver via SMTP
    - support dry-run mode
    """

    def __init__(
        self,
        *,
        to_email: str,
        dry_run: bool = False,
        smtp_host: str = config.SMTP_HOST,
        smtp_port: int = config.SMTP_PORT,
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

        if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD:
            raise RuntimeError(
                "Missing email credentials. "
                "Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD."
            )

        msg = EmailMessage()
        msg["From"] = config.GMAIL_ADDRESS
        msg["To"] = self._to_email
        msg["Subject"] = self._renderer.render_subject(changes)

        msg.set_content(self._renderer.render_text(changes))
        msg.add_alternative(
            self._renderer.render_html(changes),
            subtype="html",
        )

        if self._dry_run:
            log.info("Dry-run email to %s:\n%s", self._to_email, msg)
            return

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                if not self._dry_run:
                    try:
                        server.starttls()
                    except smtplib.SMTPNotSupportedError:
                        pass
                server.login(
                    config.GMAIL_ADDRESS,
                    config.GMAIL_APP_PASSWORD,
                )
                server.send_message(msg)
        except smtplib.SMTPException as exc:
            raise RuntimeError(
                f"Failed to send alert email to {self._to_email}"
            ) from exc
