from dataclasses import dataclass

from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange

__all__ = [
    "ScoredChange",
]


@dataclass(frozen=True)
class ScoredChange:
    """
    JobChange annotated with alert severity and explanation.

    'reason' is a short, human-readable explanation suitable for:
    - email alerts
    - CLI output
    - audit/debug logs
    """

    change: JobChange
    severity: Severity
    reason: str = ""
