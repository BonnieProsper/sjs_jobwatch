from __future__ import annotations

from datetime import date
from typing import Iterable, Dict, Any, List

from sjs_sitewatch.domain.job import Job


def normalize_jobs(raw_jobs: Iterable[Dict[str, Any]]) -> List[Job]:
    """
    Convert raw SJS job payloads into domain Job objects.

    Responsibilities:
    - Understand SJS-specific field names
    - Validate required fields
    - Perform light, explicit coercion
    - Never invent or silently corrupt data
    """

    jobs: list[Job] = []

    for raw in raw_jobs:
        job = _normalize_single(raw)
        if job is not None:
            jobs.append(job)

    return jobs


def _normalize_single(raw: Dict[str, Any]) -> Job | None:
    """
    Normalize a single raw job payload.

    Returns None if required fields are missing or invalid.
    """

    job_id = raw.get("jobId")
    title = raw.get("title")
    employer = raw.get("businessName")

    # Required field validation
    if not isinstance(job_id, (str, int)):
        return None
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(employer, str) or not employer.strip():
        return None

    return Job(
        id=str(job_id),
        title=title.strip(),
        employer=employer.strip(),
        summary=_to_str(raw.get("summary")),
        description=_to_str(raw.get("description")),
        category=_to_str(raw.get("category")),
        classification=_to_str(raw.get("classification")),
        sub_classification=_to_str(raw.get("subClassification")),
        job_type=_to_str(raw.get("jobType")),
        region=_to_str(raw.get("regionName")),
        area=_to_str(raw.get("areaName")),
        pay_min=_to_float(raw.get("payMin")),
        pay_max=_to_float(raw.get("payMax")),
        posted_date=_to_date(raw.get("postedDate")),
        start_date=_to_date(raw.get("startDate")),
        end_date=_to_date(raw.get("endDate")),
    )


# -------------------------
# Coercion helpers
# -------------------------

def _to_str(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return None


def _to_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _to_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
