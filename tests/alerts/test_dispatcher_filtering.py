from sjs_sitewatch.alerts.dispatcher import AlertDispatcher
from sjs_sitewatch.alerts.models import ScoredChange
from sjs_sitewatch.alerts.severity import Severity
from sjs_sitewatch.domain.diff import JobChange


def test_min_severity_filtering():
    dispatcher = AlertDispatcher()

    changes = [
        ScoredChange(
            change=JobChange("1", None, None, []),
            severity=Severity.LOW,
        ),
        ScoredChange(
            change=JobChange("2", None, None, []),
            severity=Severity.MEDIUM,
        ),
        ScoredChange(
            change=JobChange("3", None, None, []),
            severity=Severity.HIGH,
        ),
    ]
    # TODO
    filtered = dispatcher.filter_min_severity(
        changes,
        min_severity=Severity.MEDIUM,
    )

    severities = [c.severity for c in filtered]

    assert severities == [Severity.MEDIUM, Severity.HIGH]
