from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from sjs_sitewatch.alerts.models import ScoredChange


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _require_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        ) from exc


class EmailSink:
    """
    Email delivery sink.

    Assumes changes are already scored and filtered.
    """

    def __init__(self, *, to_email: str, dry_run: bool = False) -> None:
        self._to_email = to_email
        self._dry_run = dry_run

    def send(self, changes: Iterable[ScoredChange]) -> None:
        changes = list(changes)
        if not changes:
            return

        msg = EmailMessage()
        msg["Subject"] = f"SJS SiteWatch: {len(changes)} update(s)"
        msg["To"] = self._to_email

        body = "\n".join(
            f"[{c.severity.name}] {c.change.job_id} — {c.reason}"
            for c in changes
        )

        msg.set_content(body)

        if self._dry_run:
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
