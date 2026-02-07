"""
Email provider factory.

Constructs the appropriate email provider based on configuration.
Centralizes provider instantiation logic.
"""

import logging
from typing import Optional

from sjs_jobwatch.core import config
from sjs_jobwatch.delivery import EmailProvider
from sjs_jobwatch.delivery.providers import ConsoleProvider, ResendProvider

logger = logging.getLogger(__name__)


def get_email_provider(dry_run: bool = False) -> EmailProvider:
    """
    Get configured email provider.

    Reads EMAIL_PROVIDER from config and instantiates the appropriate
    provider with its required credentials.

    Args:
        dry_run: If True, always return ConsoleProvider regardless of config

    Returns:
        Configured email provider ready to send

    Raises:
        ValueError: If provider is unknown or misconfigured
    """
    if dry_run:
        logger.info("Using console provider (dry run mode)")
        return ConsoleProvider()

    provider_name = config.EMAIL_PROVIDER.lower()

    if provider_name == "console":
        logger.info("Using console provider")
        return ConsoleProvider()

    if provider_name == "resend":
        if not config.RESEND_API_KEY:
            raise ValueError("RESEND_API_KEY not set. " "Get one at https://resend.com/api-keys")
        if not config.EMAIL_FROM:
            raise ValueError("EMAIL_FROM not set")

        logger.info(f"Using Resend provider (from: {config.EMAIL_FROM})")
        return ResendProvider(
            api_key=config.RESEND_API_KEY,
            from_email=config.EMAIL_FROM,
        )

    if provider_name == "smtp":
        # Legacy SMTP support - import here to avoid circular dependency
        from sjs_jobwatch.delivery.legacy import SMTPProvider

        logger.warning("Using legacy SMTP provider (consider migrating to Resend)")
        return SMTPProvider(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            use_tls=config.SMTP_USE_TLS,
            username=config.GMAIL_ADDRESS,
            password=config.GMAIL_APP_PASSWORD,
            from_email=config.GMAIL_ADDRESS or "",
        )

    raise ValueError(
        f"Unknown email provider: {provider_name}. " f"Valid options: console, resend, smtp"
    )
