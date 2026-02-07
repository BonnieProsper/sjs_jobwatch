"""
Email alert delivery system.

Handles rendering and sending email notifications for job changes.
"""

import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template

from sjs_jobwatch.core import config
from sjs_jobwatch.core.models import DiffResult

logger = logging.getLogger(__name__)

# Get the templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailRenderer:
    """Renders email content from templates."""

    def __init__(self) -> None:
        """Initialize the email renderer with Jinja2 templates."""
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

    def render_html(self, diff: DiffResult, max_jobs: int = 50) -> str:
        """
        Render HTML email body.
        
        Args:
            diff: Diff result to render
            max_jobs: Maximum jobs to include per section
            
        Returns:
            HTML string
        """
        template = self.env.get_template("alert_email.html")
        return template.render(
            period=self._get_period_description(diff),
            added_count=len(diff.added),
            removed_count=len(diff.removed),
            modified_count=len(diff.modified),
            total_changes=diff.total_changes,
            added=diff.added[:max_jobs],
            removed=diff.removed[:max_jobs],
            modified=diff.modified[:max_jobs],
        )

    def render_text(self, diff: DiffResult, max_jobs: int = 50) -> str:
        """
        Render plain text email body.
        
        Args:
            diff: Diff result to render
            max_jobs: Maximum jobs to include per section
            
        Returns:
            Plain text string
        """
        template = self.env.get_template("alert_email.txt")
        return template.render(
            period=self._get_period_description(diff),
            added_count=len(diff.added),
            removed_count=len(diff.removed),
            modified_count=len(diff.modified),
            total_changes=diff.total_changes,
            added=diff.added[:max_jobs],
            removed=diff.removed[:max_jobs],
            modified=diff.modified[:max_jobs],
        )

    def render_subject(self, diff: DiffResult) -> str:
        """
        Generate email subject line.
        
        Args:
            diff: Diff result
            
        Returns:
            Subject string
        """
        if diff.total_changes == 0:
            return "SJS JobWatch: No Changes"

        parts = []
        if diff.added:
            parts.append(f"{len(diff.added)} new")
        if diff.removed:
            parts.append(f"{len(diff.removed)} removed")
        if diff.modified:
            parts.append(f"{len(diff.modified)} modified")

        return f"SJS JobWatch: {', '.join(parts)} jobs"

    @staticmethod
    def _get_period_description(diff: DiffResult) -> str:
        """Get a description of the time period covered by the diff."""
        prev_time = diff.previous_snapshot.timestamp
        curr_time = diff.current_snapshot.timestamp

        prev_str = prev_time.strftime("%B %d, %Y at %I:%M %p")
        curr_str = curr_time.strftime("%B %d, %Y at %I:%M %p")

        return f"Changes from {prev_str} to {curr_str}"


class EmailSender:
    """Sends email alerts via SMTP."""

    def __init__(
        self,
        smtp_host: str = config.SMTP_HOST,
        smtp_port: int = config.SMTP_PORT,
        use_tls: bool = config.SMTP_USE_TLS,
        dry_run: bool = False,
    ) -> None:
        """
        Initialize email sender.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            use_tls: Whether to use TLS encryption
            dry_run: If True, don't actually send emails (just log)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.use_tls = use_tls
        self.dry_run = dry_run
        self.renderer = EmailRenderer()

    def send_alert(
        self,
        to_email: str,
        diff: DiffResult,
        max_jobs: int = config.MAX_JOBS_IN_EMAIL,
    ) -> bool:
        """
        Send an alert email for a diff.
        
        Args:
            to_email: Recipient email address
            diff: Diff to send alert about
            max_jobs: Maximum jobs to include
            
        Returns:
            True if email was sent successfully
        """
        # Skip if no changes
        if not diff.has_changes:
            logger.info(f"No changes to report to {to_email}, skipping email")
            return False

        # Validate credentials
        if not self.dry_run:
            is_valid, error = config.validate_email_config()
            if not is_valid:
                logger.error(f"Invalid email configuration: {error}")
                return False

        # Create email message
        msg = EmailMessage()
        msg["From"] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM}>"
        msg["To"] = to_email
        msg["Subject"] = self.renderer.render_subject(diff)

        # Set body (text + HTML)
        msg.set_content(self.renderer.render_text(diff, max_jobs))
        msg.add_alternative(self.renderer.render_html(diff, max_jobs), subtype="html")

        # Send or log
        if self.dry_run:
            logger.info(f"[DRY RUN] Would send email to {to_email}:")
            logger.info(f"  Subject: {msg['Subject']}")
            logger.info(f"  Changes: {diff.total_changes} total")
            return True

        try:
            self._send_message(msg)
            logger.info(f"Sent alert email to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def _send_message(self, msg: EmailMessage) -> None:
        """
        Actually send an email message via SMTP.
        
        Args:
            msg: Email message to send
            
        Raises:
            Exception if sending fails
        """
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            if self.use_tls:
                server.starttls()

            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.send_message(msg)
