from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Job:
    """
    Immutable domain representation of a job listing.
    """

    # Identity (must always exist)
    id: str
    title: str

    # Core display fields
    employer: Optional[str]
    summary: Optional[str]
    description: Optional[str]

    # Classification
    category: Optional[str]
    classification: Optional[str]
    sub_classification: Optional[str]
    job_type: Optional[str]

    # Location
    region: Optional[str]
    area: Optional[str]

    # Pay
    pay_min: Optional[float]
    pay_max: Optional[float]

    # Dates
    posted_date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Job.id must be non-empty")
        if not self.title:
            raise ValueError("Job.title must be non-empty")
