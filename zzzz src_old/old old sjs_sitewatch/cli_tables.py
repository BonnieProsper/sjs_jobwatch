from rich.console import Console
from rich.table import Table

from sjs_sitewatch.ingestion.normalize import Job

console = Console()


def jobs_table(title: str, jobs: list[Job]) -> None:
    table = Table(title=title)

    table.add_column("Title")
    table.add_column("Region")
    table.add_column("Employer")

    for job in jobs:
        table.add_row(
            job.title,
            job.region or "—",
            job.employer or "—",
        )

    console.print(table)
