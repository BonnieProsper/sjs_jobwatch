from datetime import date

from sjs_sitewatch.alerts.email import send_email_alert
from sjs_sitewatch.domain.diff import diff_snapshots
from sjs_sitewatch.domain.job import Job


# -------------------------
# Fake snapshot data
# -------------------------

previous = {
    "1": Job(
        id="1",
        title="Junior Developer",
        employer="ABC Corp",
        summary="Work on internal tools",
        description=None,
        category="IT",
        classification=None,
        sub_classification=None,
        job_type="Full time",
        region="Auckland",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=None,
        start_date=None,
        end_date=None,
    )
}

current = {
    "1": Job(
        id="1",
        title="Junior Software Developer",
        employer="ABC Corp",
        summary="Work on internal tools",
        description=None,
        category="IT",
        classification=None,
        sub_classification=None,
        job_type="Full time",
        region="Auckland",
        area=None,
        pay_min=None,
        pay_max=None,
        posted_date=None,
        start_date=None,
        end_date=None,
    )
}

# -------------------------
# Diff + email
# -------------------------

diff = diff_snapshots(previous, current)

# Test 1: dry run (prints email)
send_email_alert(diff, dry_run=True)

# Test 2: real email (uncomment when ready)
# send_email_alert(diff)
