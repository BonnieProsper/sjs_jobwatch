from __future__ import annotations

import click

from sjs_sitewatch.cli.run import run
from sjs_sitewatch.cli.alerts import alerts
from sjs_sitewatch.cli.export import export


@click.group()
def main() -> None:
    """Track changes in the SJS job market over time."""
    pass


main.add_command(run)
main.add_command(alerts)
main.add_command(export)

if __name__ == "__main__":
    main()