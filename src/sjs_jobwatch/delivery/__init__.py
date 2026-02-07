"""
Email delivery providers.

Abstraction layer for sending transactional emails. Supports multiple
backends (Resend, Postmark, console output) without changing business logic.
"""

from typing import Protocol


class EmailProvider(Protocol):
    """
    Protocol for email delivery backends.

    Implementations must provide a send() method that delivers email
    to a recipient. The return value indicates success/failure.
    """

    def send(self, to: str, subject: str, html: str, text: str) -> bool:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject line
            html: HTML version of email body
            text: Plain text version of email body

        Returns:
            True if email was delivered successfully, False otherwise
        """
        ...
