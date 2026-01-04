from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import List

from sjs_sitewatch.domain.diff import DiffResult, JobChange
from sjs_sitewatch.alerts.filters import filter_ict
from sjs_sitewatch.alerts.renderer import AlertRenderer


# -------------------------
# Configuration
# -------------------------

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _require_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        ) from exc


def _get_email_config() -> tuple[str, str]:
    address = _require_env("GMAIL_ADDRESS")
    password = _require_env("GMAIL_APP_PASSWORD")
    return address, password


# -------------------------
# Filtering
# -------------------------

def _extract_relevant_jobs(diff: DiffResult) -> List[JobChange]:
    """
    Extract ICT-related job changes from a diff.
    """
    relevant: List[JobChange] = []

    for change in diff.added + diff.modified:
        job = change.after
        if job and filter_ict([job]):
            relevant.append(change)

    return relevant


# -------------------------
# Core alert logic
# -------------------------

def send_email_alert(
    diff: DiffResult,
    *,
    to_email: str,
    dry_run: bool = False,
) -> None:
    """
    Send an email alert for relevant job changes.

    If dry_run=True, prints the email instead of sending.
    """
    relevant_changes = _extract_relevant_jobs(diff)

    if not relevant_changes:
        return

    renderer = AlertRenderer()

    subject = renderer.render_subject(relevant_changes)
    text_body = renderer.render_text(relevant_changes)
    html_body = renderer.render_html(relevant_changes)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = to_email

    # Plain-text fallback
    msg.set_content(text_body)

    # HTML version
    msg.add_alternative(html_body, subtype="html")

    if dry_run:
        print("=== EMAIL (dry run) ===")
        print(msg)
        print("======================")
        return

    sender, password = _get_email_config()
    msg["From"] = sender

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)


# NEW FILE, TODO: CONSOLIDATE

from sjs_sitewatch.alerts.renderer import AlertRenderer
from sjs_sitewatch.alerts.models import ScoredChange


def send_email_alert(
    changes: list[ScoredChange],
    to_email: str,
    *,
    dry_run: bool = False,
) -> None:
    renderer = AlertRenderer()

    subject = renderer.render_subject(changes)
    body = renderer.render_html(changes)

    if dry_run:
        print("EMAIL (dry run)")
        print(subject)
        print(body)
        return

    # SMTP integration later
