"""
Resend email provider implementation.

Uses Resend's transactional email API for reliable delivery.
Requires RESEND_API_KEY environment variable.
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ResendProvider:
    """
    Email delivery via Resend API.

    Resend is a transactional email service with a clean API and
    generous free tier (3,000 emails/month). No SMTP required.

    See: https://resend.com/docs/api-reference/emails/send-email
    """

    def __init__(self, api_key: str, from_email: str) -> None:
        """
        Initialize Resend provider.

        Args:
            api_key: Resend API key (starts with 're_')
            from_email: Sender email address (must be verified domain)
        """
        self.api_key = api_key
        self.from_email = from_email
        self.api_url = "https://api.resend.com/emails"

    def send(self, to: str, subject: str, html: str, text: str) -> bool:
        """Send email via Resend API."""
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": self.from_email,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                    "text": text,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                email_id = data.get("id", "unknown")
                logger.info(f"Email sent via Resend (id: {email_id})")
                return True

            # Log error details
            logger.error(f"Resend API error: {response.status_code} - {response.text}")
            return False

        except requests.RequestException as e:
            logger.error(f"Failed to send via Resend: {e}")
            return False


class ConsoleProvider:
    """
    Console output provider for development/testing.

    Logs email content instead of sending. Useful for:
    - Local development without API keys
    - Testing email rendering
    - Dry-run modes
    """

    def send(self, to: str, subject: str, html: str, text: str) -> bool:
        """Log email to console instead of sending."""
        logger.info("=" * 70)
        logger.info("EMAIL (Console Provider - Not Actually Sent)")
        logger.info("=" * 70)
        logger.info(f"To: {to}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 70)
        logger.info("Plain Text Body:")
        logger.info(text[:500])  # First 500 chars
        if len(text) > 500:
            logger.info(f"... ({len(text) - 500} more characters)")
        logger.info("=" * 70)
        return True
