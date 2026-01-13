from __future__ import annotations

import click

from sjs_sitewatch.cli.run import run
from sjs_sitewatch.cli.alerts import alerts
from sjs_sitewatch.cli.export import export


@click.group()
def cli() -> None:
    """Track changes in the SJS job market over time."""
    pass


cli.add_command(run)
cli.add_command(alerts)
cli.add_command(export)
