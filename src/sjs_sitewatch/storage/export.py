from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
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


def export_jobs_csv(jobs: Iterable[Job], path: Path) -> None:
    """
    Export jobs to CSV using domain field order.
    """
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_FIELDS)

        for job in jobs:
            writer.writerow(
                _serialize(getattr(job, field))
                for field in _FIELDS
            )


def export_jobs_json(jobs: Iterable[Job], path: Path) -> None:
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

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
