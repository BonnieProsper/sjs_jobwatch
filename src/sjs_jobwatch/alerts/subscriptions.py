"""
Subscription management for email alerts.

Handles user subscriptions for job change notifications.
"""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from sjs_jobwatch.core import config
from sjs_jobwatch.core.models import Frequency, JobCategory, Region, Severity

logger = logging.getLogger(__name__)


class AlertSubscription(BaseModel):
    """
    Represents a user's subscription to job alerts.

    Defines what changes they want to be notified about and how often.
    """

    email: str = Field(..., description="Email address to send alerts to")

    # Filters
    region: Region | None = Field(
        None,
        description="Only alert about jobs in this region (None = all regions)",
    )
    category: JobCategory | None = Field(
        None,
        description="Only alert about jobs in this category (None = all categories)",
    )
    min_severity: Severity = Field(
        default=Severity.MEDIUM,
        description="Minimum severity level to trigger alert",
    )

    # Schedule
    frequency: Frequency = Field(
        default=Frequency.DAILY,
        description="How often to send alerts",
    )
    hour: int = Field(
        default=9,
        ge=0,
        le=23,
        description="Hour of day to send alerts (0-23, UTC)",
    )

    # Features
    include_descriptions: bool = Field(
        default=False,
        description="Include full job descriptions in emails",
    )
    max_jobs_per_email: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of jobs to include per email",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Ensure email looks valid."""
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError(f"Invalid email address: {v}")
        return v

    def matches_job(self, job: Any) -> bool:
        """
        Check if a job matches this subscription's filters.

        Args:
            job: Job object to check

        Returns:
            True if job matches filters
        """
        # Check region filter
        if self.region is not None and self.region != Region.ALL:
            if not hasattr(job, "region") or job.region != self.region.value:
                return False

        # Check category filter
        if self.category is not None and self.category != JobCategory.ALL:
            if not hasattr(job, "category") or job.category != self.category.value:
                return False

        return True


class SubscriptionStore:
    """
    Storage for alert subscriptions.

    Stores subscriptions as a JSON file for simplicity.
    In production, this might be a database.
    """

    def __init__(self, filepath: Path | None = None) -> None:
        """
        Initialize subscription storage.

        Args:
            filepath: Path to subscriptions file (defaults to config.SUBSCRIPTIONS_FILE)
        """
        self.filepath = filepath or config.SUBSCRIPTIONS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create an empty subscriptions file if it doesn't exist."""
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath.write_text("[]", encoding="utf-8")
            logger.info(f"Created new subscriptions file: {self.filepath}")

    def load_all(self) -> list[AlertSubscription]:
        """
        Load all subscriptions from disk.

        Returns:
            List of subscriptions
        """
        try:
            data = json.loads(self.filepath.read_text(encoding="utf-8"))
            subscriptions = [AlertSubscription(**item) for item in data]
            logger.debug(f"Loaded {len(subscriptions)} subscriptions")
            return subscriptions
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in subscriptions file: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load subscriptions: {e}")
            return []

    def save_all(self, subscriptions: list[AlertSubscription]) -> None:
        """
        Save all subscriptions to disk.

        Args:
            subscriptions: List of subscriptions to save
        """
        try:
            data = [sub.model_dump(mode="json") for sub in subscriptions]
            self.filepath.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info(f"Saved {len(subscriptions)} subscriptions")
        except Exception as e:
            logger.error(f"Failed to save subscriptions: {e}")
            raise

    def add(self, subscription: AlertSubscription) -> None:
        """
        Add a new subscription.

        If subscription with same email already exists, it's replaced.

        Args:
            subscription: Subscription to add
        """
        subscriptions = self.load_all()

        # Remove existing subscription for this email
        subscriptions = [sub for sub in subscriptions if sub.email != subscription.email]

        # Add new subscription
        subscriptions.append(subscription)

        self.save_all(subscriptions)
        logger.info(f"Added subscription for {subscription.email}")

    def remove(self, email: str) -> bool:
        """
        Remove a subscription by email.

        Args:
            email: Email address to remove

        Returns:
            True if subscription was removed, False if not found
        """
        email = email.strip().lower()
        subscriptions = self.load_all()
        original_count = len(subscriptions)

        subscriptions = [sub for sub in subscriptions if sub.email != email]

        if len(subscriptions) < original_count:
            self.save_all(subscriptions)
            logger.info(f"Removed subscription for {email}")
            return True

        logger.warning(f"No subscription found for {email}")
        return False

    def get(self, email: str) -> AlertSubscription | None:
        """
        Get a subscription by email.

        Args:
            email: Email to look up

        Returns:
            Subscription or None if not found
        """
        email = email.strip().lower()
        for sub in self.load_all():
            if sub.email == email:
                return sub
        return None

    def list_emails(self) -> list[str]:
        """
        Get list of all subscribed email addresses.

        Returns:
            List of emails
        """
        return [sub.email for sub in self.load_all()]
