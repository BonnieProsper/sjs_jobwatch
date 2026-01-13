"""
CLI commands for managing alert subscriptions.

This module is intentionally separate from alert execution
and scheduling logic.
"""
from __future__ import annotations

import click
from pathlib import Path

from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.users.models import AlertSubscription
from sjs_sitewatch.users.store import SubscriptionStore


DEFAULT_STORE = Path("subscriptions.json")


@click.group()
def alerts() -> None:
    """Manage email alert subscriptions."""
    pass


# -------------------------
# Add subscription
# -------------------------

@alerts.command()
@click.option("--email", required=True)
@click.option("--ict-only/--all", default=True)
@click.option("--region", default=None)
@click.option(
    "--frequency",
    type=click.Choice(["daily", "weekly"]),
    default="daily",
)
@click.option("--hour", type=int, default=12)
@click.option(
    "--min-severity",
    type=click.Choice([s.value for s in Severity]),
    default=Severity.MEDIUM.value,
    help="Minimum severity required to trigger an alert",
)
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE,
)
def add(email, ict_only, region, frequency, hour, min_severity, store):
    """Add a new alert subscription."""
    subscription = AlertSubscription(
        email=email,
        ict_only=ict_only,
        region=region,
        frequency=frequency,
        hour=hour,
        min_severity=Severity(min_severity),
    )
    subscription.validate()

    store = SubscriptionStore(store)
    subs = store.load_all()

    if any(s.email == email for s in subs):
        raise click.ClickException("Subscription already exists for this email")

    subs.append(subscription)
    store.save_all(subs)

    click.echo("✅ Alert subscription registered")


# -------------------------
# List subscriptions
# -------------------------

@alerts.command(name="list")
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE,
)
def list_subscriptions(store):
    """List all alert subscriptions."""
    store = SubscriptionStore(store)
    subs = store.load_all()

    if not subs:
        click.echo("No subscriptions found.")
        return

    for sub in subs:
        click.echo(
            f"- {sub.email} | "
            f"{'ICT only' if sub.ict_only else 'All jobs'} | "
            f"{sub.region or 'All regions'} | "
            f"{sub.frequency} @ {sub.hour}:00 | "
            f"min severity: {sub.min_severity.value}"
        )


# -------------------------
# Edit subscription
# -------------------------

@alerts.command()
@click.option("--email", required=True)
@click.option("--ict-only/--all", default=None)
@click.option("--region", default=None)
@click.option(
    "--frequency",
    type=click.Choice(["daily", "weekly"]),
    default=None,
)
@click.option("--hour", type=int, default=None)
@click.option(
    "--min-severity",
    type=click.Choice([s.value for s in Severity]),
    default=None,
)
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE,
)
def edit(email, ict_only, region, frequency, hour, min_severity, store):
    """Edit an existing alert subscription."""
    store = SubscriptionStore(store)
    subs = store.load_all()

    for i, sub in enumerate(subs):
        if sub.email != email:
            continue

        updated = AlertSubscription(
            email=sub.email,
            ict_only=sub.ict_only if ict_only is None else ict_only,
            region=sub.region if region is None else region,
            frequency=sub.frequency if frequency is None else frequency,
            hour=sub.hour if hour is None else hour,
            min_severity=(
                sub.min_severity
                if min_severity is None
                else Severity(min_severity)
            ),
        )
        updated.validate()

        subs[i] = updated
        store.save_all(subs)

        click.echo("✏️ Subscription updated")
        return

    raise click.ClickException("No subscription found for this email")


# -------------------------
# Remove subscription
# -------------------------

@alerts.command()
@click.option("--email", required=True)
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE,
)
def remove(email, store):
    """Remove an alert subscription."""
    store = SubscriptionStore(store)
    subs = store.load_all()

    new_subs = [s for s in subs if s.email != email]

    if len(new_subs) == len(subs):
        raise click.ClickException("No subscription found for this email")

    store.save_all(new_subs)
    click.echo("🗑️ Subscription removed")
