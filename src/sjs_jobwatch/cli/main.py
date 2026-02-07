"""
Main CLI entry point for SJS JobWatch.

Provides commands for scraping, viewing diffs, managing subscriptions, and running alerts.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from sjs_jobwatch.alerts.email import EmailSender
from sjs_jobwatch.alerts.subscriptions import AlertSubscription, SubscriptionStore
from sjs_jobwatch.core import config
from sjs_jobwatch.core.diff import diff_snapshots, summarize_diff
from sjs_jobwatch.core.models import Frequency, JobCategory, Region, Severity
from sjs_jobwatch.ingestion.scraper import scrape_sjs_jobs
from sjs_jobwatch.storage.snapshots import SnapshotStore

console = Console()

# ============================================================================
# Logging Setup
# ============================================================================


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.LOG_FILE),
        ],
    )


# ============================================================================
# Main CLI Group
# ============================================================================


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    SJS JobWatch - Monitor and track changes in the SJS New Zealand job board.
    
    Use 'sjs-jobwatch COMMAND --help' for help on specific commands.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)
    config.ensure_directories()


# ============================================================================
# Scrape Command
# ============================================================================


@cli.command()
@click.option(
    "--region",
    type=click.Choice([r.value for r in Region], case_sensitive=False),
    default="All",
    help="Filter by region",
)
@click.option(
    "--category",
    type=click.Choice([c.value for c in JobCategory], case_sensitive=False),
    default="All",
    help="Filter by category",
)
@click.option("--keyword", default="", help="Search keyword")
@click.pass_context
def scrape(ctx: click.Context, region: str, category: str, keyword: str) -> None:
    """Scrape current jobs from the SJS website and save a snapshot."""
    console.print(f"[bold blue]Scraping SJS jobs...[/bold blue]")
    console.print(f"  Region: {region}")
    console.print(f"  Category: {category}")
    if keyword:
        console.print(f"  Keyword: {keyword}")

    try:
        # Scrape jobs
        snapshot = scrape_sjs_jobs(region=region, category=category, keyword=keyword)

        # Save snapshot
        store = SnapshotStore()
        filepath = store.save(snapshot)

        console.print(f"[green]✓[/green] Scraped {len(snapshot.jobs)} jobs")
        console.print(f"[green]✓[/green] Saved snapshot to {filepath}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        sys.exit(1)


# ============================================================================
# Diff Command
# ============================================================================


@cli.command()
@click.option(
    "--since",
    type=int,
    default=1,
    help="Compare with snapshot from N snapshots ago (default: 1)",
)
@click.option("--format", type=click.Choice(["table", "text"]), default="table")
@click.pass_context
def diff(ctx: click.Context, since: int, format: str) -> None:
    """Show differences between the latest snapshot and a previous one."""
    store = SnapshotStore()
    snapshots = store.load_latest(n=since + 1)

    if len(snapshots) < 2:
        console.print("[yellow]Not enough snapshots to compare.[/yellow]")
        console.print(f"Found {len(snapshots)} snapshot(s), need at least 2.")
        return

    # Diff the snapshots
    previous = snapshots[since]
    current = snapshots[0]

    console.print(f"[bold]Comparing snapshots:[/bold]")
    console.print(f"  Previous: {previous.timestamp}")
    console.print(f"  Current:  {current.timestamp}")
    console.print()

    diff_result = diff_snapshots(previous, current)

    if format == "text":
        console.print(summarize_diff(diff_result))
    else:
        _display_diff_table(diff_result)


def _display_diff_table(diff_result) -> None:
    """Display diff result as a rich table."""
    # Summary
    table = Table(title="Summary", show_header=False)
    table.add_row("New Jobs", f"[green]{len(diff_result.added)}[/green]")
    table.add_row("Removed Jobs", f"[red]{len(diff_result.removed)}[/red]")
    table.add_row("Modified Jobs", f"[yellow]{len(diff_result.modified)}[/yellow]")
    table.add_row("Total Changes", f"[bold]{diff_result.total_changes}[/bold]")
    console.print(table)
    console.print()

    # New jobs
    if diff_result.added:
        table = Table(title="✨ New Jobs", show_lines=True)
        table.add_column("Title", style="green")
        table.add_column("Employer")
        table.add_column("Region")
        table.add_column("Category")

        for change in diff_result.added[:20]:  # Limit to 20 for readability
            job = change.after
            table.add_row(
                job.title,
                job.employer,
                job.region or "-",
                job.category or "-",
            )

        console.print(table)
        if len(diff_result.added) > 20:
            console.print(f"[dim]... and {len(diff_result.added) - 20} more[/dim]")
        console.print()

    # Removed jobs
    if diff_result.removed:
        table = Table(title="❌ Removed Jobs", show_lines=True)
        table.add_column("Title", style="red")
        table.add_column("Employer")
        table.add_column("Region")

        for change in diff_result.removed[:20]:
            job = change.before
            table.add_row(job.title, job.employer, job.region or "-")

        console.print(table)
        if len(diff_result.removed) > 20:
            console.print(f"[dim]... and {len(diff_result.removed) - 20} more[/dim]")
        console.print()

    # Modified jobs
    if diff_result.modified:
        table = Table(title="✏️  Modified Jobs", show_lines=True)
        table.add_column("Title", style="yellow")
        table.add_column("Employer")
        table.add_column("Changes")

        for change in diff_result.modified[:20]:
            job = change.after
            changes_summary = ", ".join(fc.field for fc in change.changes[:3])
            if len(change.changes) > 3:
                changes_summary += f" (+{len(change.changes) - 3} more)"

            table.add_row(job.title, job.employer, changes_summary)

        console.print(table)
        if len(diff_result.modified) > 20:
            console.print(f"[dim]... and {len(diff_result.modified) - 20} more[/dim]")


# ============================================================================
# List Command
# ============================================================================


@cli.command()
@click.option("--limit", "-n", type=int, default=10, help="Number of snapshots to show")
def list(limit: int) -> None:
    """List available snapshots."""
    store = SnapshotStore()
    files = store.list_snapshots()

    if not files:
        console.print("[yellow]No snapshots found.[/yellow]")
        return

    table = Table(title=f"Recent Snapshots (showing {min(limit, len(files))} of {len(files)})")
    table.add_column("#", justify="right")
    table.add_column("Timestamp")
    table.add_column("Jobs", justify="right")
    table.add_column("Duration", justify="right")

    for i, filepath in enumerate(files[:limit], 1):
        try:
            import json

            with open(filepath) as f:
                data = json.load(f)

            timestamp = datetime.fromisoformat(data["timestamp"])
            duration = data.get("scrape_duration_seconds", 0)

            table.add_row(
                str(i),
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                str(data["total_count"]),
                f"{duration:.1f}s" if duration else "-",
            )
        except Exception:
            continue

    console.print(table)


# ============================================================================
# Export Command
# ============================================================================


@cli.command()
@click.argument("format", type=click.Choice(["csv", "json"]))
@click.argument("output", type=click.Path())
@click.option("--snapshot", type=int, default=0, help="Which snapshot to export (0=latest)")
def export(format: str, output: str, snapshot: int) -> None:
    """Export a snapshot to CSV or JSON format."""
    store = SnapshotStore()
    snapshots = store.load_latest(n=snapshot + 1)

    if not snapshots or len(snapshots) <= snapshot:
        console.print(f"[red]Snapshot #{snapshot} not found[/red]")
        sys.exit(1)

    snap = snapshots[snapshot]
    output_path = Path(output)

    try:
        if format == "csv":
            store.export_to_csv(snap, output_path)
        else:
            store.export_to_json(snap, output_path)

        console.print(f"[green]✓[/green] Exported {len(snap.jobs)} jobs to {output_path}")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        sys.exit(1)


# ============================================================================
# Alerts Commands
# ============================================================================


@cli.group()
def alerts() -> None:
    """Manage email alert subscriptions."""
    pass


@alerts.command("add")
@click.argument("email")
@click.option("--region", type=click.Choice([r.value for r in Region]), help="Filter by region")
@click.option(
    "--category", type=click.Choice([c.value for c in JobCategory]), help="Filter by category"
)
@click.option(
    "--frequency",
    type=click.Choice([f.value for f in Frequency]),
    default="daily",
    help="Alert frequency",
)
@click.option("--hour", type=int, default=9, help="Hour of day to send (0-23, UTC)")
@click.option(
    "--severity",
    type=click.Choice([s.value for s in Severity]),
    default="medium",
    help="Minimum severity",
)
def alerts_add(
    email: str,
    region: Optional[str],
    category: Optional[str],
    frequency: str,
    hour: int,
    severity: str,
) -> None:
    """Add a new email alert subscription."""
    try:
        subscription = AlertSubscription(
            email=email,
            region=Region(region) if region else None,
            category=JobCategory(category) if category else None,
            frequency=Frequency(frequency),
            hour=hour,
            min_severity=Severity(severity),
        )

        store = SubscriptionStore()
        store.add(subscription)

        console.print(f"[green]✓[/green] Added alert subscription for {email}")
        console.print(f"  Frequency: {frequency}")
        console.print(f"  Hour: {hour}:00 UTC")
        if region:
            console.print(f"  Region: {region}")
        if category:
            console.print(f"  Category: {category}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        sys.exit(1)


@alerts.command("remove")
@click.argument("email")
def alerts_remove(email: str) -> None:
    """Remove an email alert subscription."""
    store = SubscriptionStore()

    if store.remove(email):
        console.print(f"[green]✓[/green] Removed subscription for {email}")
    else:
        console.print(f"[yellow]No subscription found for {email}[/yellow]")


@alerts.command("list")
def alerts_list() -> None:
    """List all alert subscriptions."""
    store = SubscriptionStore()
    subscriptions = store.load_all()

    if not subscriptions:
        console.print("[yellow]No alert subscriptions configured.[/yellow]")
        return

    table = Table(title=f"Alert Subscriptions ({len(subscriptions)} total)")
    table.add_column("Email")
    table.add_column("Frequency")
    table.add_column("Hour (UTC)")
    table.add_column("Region")
    table.add_column("Category")
    table.add_column("Min Severity")

    for sub in subscriptions:
        table.add_row(
            sub.email,
            sub.frequency.value,
            f"{sub.hour}:00",
            sub.region.value if sub.region else "All",
            sub.category.value if sub.category else "All",
            sub.min_severity.value,
        )

    console.print(table)


@alerts.command("test")
@click.argument("email")
@click.option("--dry-run", is_flag=True, help="Don't actually send email")
def alerts_test(email: str, dry_run: bool) -> None:
    """Test sending an alert email (uses last two snapshots)."""
    store = SnapshotStore()
    snapshots = store.load_latest(n=2)

    if len(snapshots) < 2:
        console.print("[red]Need at least 2 snapshots to test alerts[/red]")
        sys.exit(1)

    diff_result = diff_snapshots(snapshots[1], snapshots[0])

    console.print(f"Testing alert email to {email}...")
    console.print(f"Changes: {diff_result.total_changes}")

    sender = EmailSender(dry_run=dry_run)
    success = sender.send_alert(email, diff_result)

    if success:
        if dry_run:
            console.print("[green]✓[/green] Dry run successful (no email sent)")
        else:
            console.print("[green]✓[/green] Test email sent successfully")
    else:
        console.print("[red]✗[/red] Failed to send test email")
        sys.exit(1)


# ============================================================================
# Run Command (Background Service)
# ============================================================================


@cli.command()
@click.option("--dry-run", is_flag=True, help="Don't send emails, just log")
@click.option("--once", is_flag=True, help="Run once and exit (don't schedule)")
def run(dry_run: bool, once: bool) -> None:
    """
    Run the alert service (scrape and send alerts on schedule).
    
    This command will scrape jobs and send alerts according to
    configured subscriptions. Use --once to run immediately and exit,
    or run without --once to keep running on schedule.
    """
    # This is a simplified version - full scheduler implementation would
    # use APScheduler for proper cron-style scheduling
    from time import sleep

    console.print("[bold blue]Starting SJS JobWatch service...[/bold blue]")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No emails will be sent[/yellow]")

    store = SubscriptionStore()
    subscriptions = store.load_all()

    if not subscriptions:
        console.print("[yellow]No subscriptions configured. Use 'alerts add' first.[/yellow]")
        return

    console.print(f"Loaded {len(subscriptions)} subscription(s)")

    while True:
        try:
            # Scrape current jobs
            console.print("\n[bold]Scraping jobs...[/bold]")
            snapshot = scrape_sjs_jobs()

            snap_store = SnapshotStore()
            snap_store.save(snapshot)

            # Check if we have a previous snapshot to compare
            snapshots = snap_store.load_latest(n=2)

            if len(snapshots) >= 2:
                diff_result = diff_snapshots(snapshots[1], snapshots[0])

                if diff_result.has_changes:
                    console.print(f"[green]{diff_result.total_changes} changes detected[/green]")

                    # Send alerts to subscribers
                    sender = EmailSender(dry_run=dry_run)

                    for sub in subscriptions:
                        console.print(f"  Sending alert to {sub.email}...")
                        sender.send_alert(sub.email, diff_result)
                else:
                    console.print("[dim]No changes detected[/dim]")
            else:
                console.print("[dim]First snapshot - nothing to compare yet[/dim]")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

        if once:
            break

        # Wait before next run (this is simplified - real version would use scheduler)
        console.print("\n[dim]Waiting 1 hour until next check...[/dim]")
        sleep(3600)


if __name__ == "__main__":
    cli()
