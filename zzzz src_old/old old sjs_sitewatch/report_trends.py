from typing import List

from state.models import Snapshot
from sjs_sitewatch.domain.trends import rolling_job_growth


def report_rolling_growth(
    snapshots: List[Snapshot],
    days: int = 7,
) -> None:
    growth = rolling_job_growth(snapshots, days)

    print(f"\n📈 {days}-day rolling job growth")

    if growth is None:
        print("  Not enough data yet")
        return

    sign = "+" if growth >= 0 else ""
    print(f"  {sign}{growth} jobs")
