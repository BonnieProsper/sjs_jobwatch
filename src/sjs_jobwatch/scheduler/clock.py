"""
Scheduler clock abstraction.

Wraps time operations for testability.
"""

import time
from datetime import datetime


class Clock:
    """System clock - production time source."""

    def now(self) -> datetime:
        """Current datetime."""
        return datetime.now()

    def sleep(self, seconds: float) -> None:
        """Sleep for duration."""
        time.sleep(seconds)
