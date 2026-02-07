"""
Legacy SMTP email provider.

Preserved for backward compatibility with v1 Gmail-based setups.
New deployments should use Resend or another transactional provider.

This will be deprecated in a future version.
"""

import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class SMTPProvider:
    """
    SMTP email delivery (legacy v1 compatibility).

    Kept for users who have existing Gmail app password setups.
    Not recommended for new deployments - use Resend instead.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        use_tls: bool,
        username: str | None,
        password: str | None,
        from_email: str,
    ) -> None:
        """
        Initialize SMTP provider.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            use_tls: Whether to use STARTTLS
            username: SMTP authentication username
            password: SMTP authentication password
            from_email: Sender email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.from_email = from_email

    def send(self, to: str, subject: str, html: str, text: str) -> bool:
        """Send email via SMTP."""
        try:
            msg = EmailMessage()
            msg["From"] = self.from_email
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(text)
            msg.add_alternative(html, subtype="html")

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.use_tls:
                    server.starttls()

                if self.username and self.password:
                    server.login(self.username, self.password)

                server.send_message(msg)

            logger.info(f"Email sent via SMTP to {to}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send via SMTP: {e}")
            return False
