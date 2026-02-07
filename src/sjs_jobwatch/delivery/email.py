"""
Email alert delivery.

Handles rendering email content from templates and delivering via
configurable email providers. Decouples rendering logic from delivery
mechanism.
"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from sjs_jobwatch.core import config
from sjs_jobwatch.core.models import DiffResult
from sjs_jobwatch.delivery import EmailProvider

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailRenderer:
    """
    Renders email content from Jinja2 templates.

    Separates presentation logic from delivery. Produces both HTML
    and plain text versions for maximum email client compatibility.
    """

    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=True,
        )

    def render(self, diff: DiffResult, max_jobs: int = 50) -> tuple[str, str, str]:
        """
        Render email subject, HTML body, and text body.

        Args:
            diff: Job changes to include in email
            max_jobs: Maximum jobs per section (prevents massive emails)

        Returns:
            Tuple of (subject, html, text)
        """
        subject = self._render_subject(diff)
        html = self._render_html(diff, max_jobs)
        text = self._render_text(diff, max_jobs)
        return subject, html, text

    def _render_subject(self, diff: DiffResult) -> str:
        """Generate concise subject line summarizing changes."""
        if diff.total_changes == 0:
            return "SJS JobWatch: No Changes"

        parts = []
        if diff.added:
            parts.append(f"{len(diff.added)} new")
        if diff.removed:
            parts.append(f"{len(diff.removed)} removed")
        if diff.modified:
            parts.append(f"{len(diff.modified)} modified")

        return f"SJS JobWatch: {', '.join(parts)}"

    def _render_html(self, diff: DiffResult, max_jobs: int) -> str:
        """Render HTML email body from template."""
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

    def _render_text(self, diff: DiffResult, max_jobs: int) -> str:
        """Render plain text email body from template."""
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

    @staticmethod
    def _get_period_description(diff: DiffResult) -> str:
        """Format time range covered by this diff."""
        prev_time = diff.previous_snapshot.timestamp
        curr_time = diff.current_snapshot.timestamp

        prev_str = prev_time.strftime("%B %d, %Y at %I:%M %p")
        curr_str = curr_time.strftime("%B %d, %Y at %I:%M %p")

        return f"{prev_str} to {curr_str}"


class EmailSender:
    """
    Sends email alerts using pluggable providers.

    Handles:
    - Rendering email content
    - Checking for changes (don't send if nothing changed)
    - Delegating delivery to provider
    - Logging successes and failures
    """

    def __init__(self, provider: EmailProvider, dry_run: bool = False) -> None:
        """
        Initialize email sender.

        Args:
            provider: Email delivery backend (Resend, Console, etc.)
            dry_run: If True, log but don't actually send
        """
        self.provider = provider
        self.dry_run = dry_run
        self.renderer = EmailRenderer()

    def send_alert(
        self,
        to_email: str,
        diff: DiffResult,
        max_jobs: int = config.MAX_JOBS_IN_EMAIL,
    ) -> bool:
        """
        Send alert email for job changes.

        Args:
            to_email: Recipient email address
            diff: Job changes to report
            max_jobs: Maximum jobs to include per section

        Returns:
            True if sent successfully, False otherwise
        """
        # Skip if no changes
        if not diff.has_changes:
            logger.info(f"No changes for {to_email}, skipping email")
            return False

        # Render email content
        subject, html, text = self.renderer.render(diff, max_jobs)

        # Dry run: log but don't send
        if self.dry_run:
            logger.info(f"[DRY RUN] Would send to {to_email}:")
            logger.info(f"  Subject: {subject}")
            logger.info(f"  Changes: {diff.total_changes} total")
            return True

        # Send via provider
        try:
            success = self.provider.send(to_email, subject, html, text)
            if success:
                logger.info(f"Alert sent to {to_email}")
            else:
                logger.error(f"Provider failed to send to {to_email}")
            return success

        except Exception as e:
            logger.error(f"Error sending to {to_email}: {e}", exc_info=True)
            return False
