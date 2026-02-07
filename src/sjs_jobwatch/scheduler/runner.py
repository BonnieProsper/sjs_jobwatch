"""
Scheduler service runner.

Main loop that wakes periodically, checks subscriptions,
and runs jobs when due. Handles shutdown gracefully.
"""

import logging
import signal
from datetime import datetime
from typing import Callable

from sjs_jobwatch.scheduler.clock import Clock
from sjs_jobwatch.scheduler.policy import check_interval, should_run

logger = logging.getLogger(__name__)


class Runner:
    """
    Service runner - main scheduler loop.

    Runs continuously until stopped, checking subscriptions
    and executing jobs on schedule.
    """

    def __init__(self, clock: Clock | None = None) -> None:
        """
        Initialize runner.

        Args:
            clock: Time source (defaults to system clock)
        """
        self.clock = clock or Clock()
        self.running = False
        self._setup_signals()

    def _setup_signals(self) -> None:
        """Configure graceful shutdown on SIGINT/SIGTERM."""

        def handler(signum: int, frame) -> None:
            logger.info("Shutdown signal received")
            self.running = False

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def run(
        self,
        check_subscriptions: Callable[[], list[tuple[str, datetime | None, str, int]]],
        run_job: Callable[[str], None],
        update_last_run: Callable[[str, datetime], None],
    ) -> None:
        """
        Main service loop.

        Args:
            check_subscriptions: Function that returns list of (email, last_run, freq, hour)
            run_job: Function to run job for an email
            update_last_run: Function to record when job ran
        """
        self.running = True
        logger.info("Scheduler started")

        while self.running:
            try:
                # Get current subscriptions
                subs = check_subscriptions()
                now = self.clock.now()

                # Check each subscription
                for email, last_run, frequency, target_hour in subs:
                    if should_run(last_run, frequency, target_hour, now):
                        logger.info(f"Running job for {email}")
                        try:
                            run_job(email)
                            update_last_run(email, now)
                        except Exception as e:
                            logger.error(f"Job failed for {email}: {e}", exc_info=True)

                # Sleep until next check
                interval = check_interval(len(subs))
                logger.debug(f"Sleeping {interval}s until next check")
                self._sleep_interruptible(interval)

            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                self._sleep_interruptible(60)

        logger.info("Scheduler stopped")

    def _sleep_interruptible(self, seconds: int) -> None:
        """
        Sleep but wake every second to check shutdown flag.

        Allows quick shutdown response instead of waiting for
        full sleep duration.
        """
        for _ in range(seconds):
            if not self.running:
                break
            self.clock.sleep(1)

    def stop(self) -> None:
        """Request shutdown (for tests/external control)."""
        self.running = False
