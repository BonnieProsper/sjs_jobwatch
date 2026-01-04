from dataclasses import dataclass

from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange


@dataclass(frozen=True)
class ScoredChange:
    """
    JobChange annotated with alert severity.
    """
    change: JobChange
    severity: Severity
