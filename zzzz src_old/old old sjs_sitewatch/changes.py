from typing import List

from sjs_sitewatch.ingestion.normalize import Job


FIELDS_TO_TRACK = {
    "title": "Title",
    "summary": "Summary",
    "state": "State",
    "region": "Region",
    "area": "Area",
    "job_type": "Job type",
    "employer": "Employer",
}


def explain_job_changes(old: Job, new: Job) -> List[str]:
    changes = []

    for field, label in FIELDS_TO_TRACK.items():
        old_value = getattr(old, field)
        new_value = getattr(new, field)

        if old_value != new_value:
            changes.append(
                f"{label} changed from '{old_value}' → '{new_value}'"
            )

    return changes
