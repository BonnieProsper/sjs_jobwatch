from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from .job import Job


@dataclass(frozen=True)
class Snapshot:
    """
    Immutable snapshot of job listings at a point in time.

    Snapshots are append-only and never mutated.
    """
    captured_at: datetime
    jobs: Dict[str, Job]  # keyed by Job.id
