from __future__ import annotations

import csv
import json
from datetime import date
from typing import Iterable, Any

from sjs_sitewatch.domain.job import Job


_FIELDS = tuple(Job.__dataclass_fields__.keys())


def _serialize(value: Any) -> Any:
    """
    Convert domain values into JSON/CSV-safe representations.
    """
    if isinstance(value, date):
        return value.isoformat()
    return value


def export_csv(jobs: Iterable[Job], path: str) -> None:
    """
    Export jobs to CSV using domain field order.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_FIELDS)

        for job in jobs:
            writer.writerow(
                _serialize(getattr(job, field))
                for field in _FIELDS
            )


def export_json(jobs: Iterable[Job], path: str) -> None:
    """
    Export jobs to JSON with safe serialization.
    """
    payload = [
        {
            field: _serialize(getattr(job, field))
            for field in _FIELDS
        }
        for job in jobs
    ]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
