"""
Scheduling policy.

Pure functions that decide when subscriptions should run.
No I/O, no side effects - just logic.
"""

from datetime import datetime, timedelta


def should_run(
    last_run: datetime | None,
    frequency: str,
    target_hour: int,
    now: datetime,
) -> bool:
    """
    Decide if subscription should run now.

    Rules:
    - Never run before: yes
    - Daily: once per day at target hour
    - Weekly: Mondays at target hour

    Args:
        last_run: When subscription last ran (None if never)
        frequency: "daily" or "weekly"
        target_hour: Hour to run (0-23)
        now: Current time

    Returns:
        True if should run now
    """
    if last_run is None:
        return True

    if frequency == "daily":
        return _daily_check(last_run, target_hour, now)

    if frequency == "weekly":
        return _weekly_check(last_run, target_hour, now)

    return False


def _daily_check(last_run: datetime, target_hour: int, now: datetime) -> bool:
    """Check if daily subscription is due."""
    # Require at least 23 hours gap
    gap = now - last_run
    if gap < timedelta(hours=23):
        return False

    # Must be past target hour today
    if now.hour < target_hour:
        return False

    # Don't run twice on same day
    if last_run.date() == now.date():
        return False

    return True


def _weekly_check(last_run: datetime, target_hour: int, now: datetime) -> bool:
    """Check if weekly subscription is due."""
    # Require at least 6 days gap
    gap = now - last_run
    if gap < timedelta(days=6):
        return False

    # Must be Monday
    if now.weekday() != 0:
        return False

    # Must be past target hour
    if now.hour < target_hour:
        return False

    return True


def check_interval(subscription_count: int) -> int:
    """
    How often to wake up and check.

    Balances responsiveness vs resource usage.

    Args:
        subscription_count: Number of active subscriptions

    Returns:
        Seconds between checks
    """
    if subscription_count == 0:
        return 3600  # 1 hour if idle

    if subscription_count < 10:
        return 900  # 15 min

    return 600  # 10 min for busy systems
