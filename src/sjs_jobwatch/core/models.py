"""
Core domain models for the SJS JobWatch application.

These models represent the fundamental business entities and are designed to be:
- Immutable by default
- Validated on construction
- Serializable to/from JSON
- Type-safe
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Region(str, Enum):
    """New Zealand regions available on SJS job board."""

    ALL = "All"
    AUCKLAND = "Auckland"
    BAY_OF_PLENTY = "Bay of Plenty"
    CANTERBURY = "Canterbury"
    GISBORNE = "Gisborne"
    HAWKES_BAY = "Hawke's Bay"
    MANAWATU_WANGANUI = "Manawatu-Wanganui"
    MARLBOROUGH = "Marlborough"
    NELSON = "Nelson"
    NORTHLAND = "Northland"
    OTAGO = "Otago"
    SOUTHLAND = "Southland"
    TARANAKI = "Taranaki"
    TASMAN = "Tasman"
    WAIKATO = "Waikato"
    WELLINGTON = "Wellington"
    WEST_COAST = "West Coast"
    OVERSEAS = "Overseas"


class JobCategory(str, Enum):
    """Main job categories on SJS."""

    ALL = "All"
    ICT = "ICT"
    ALLIED_HEALTH = "Allied Health"
    CORPORATE = "Corporate"
    EDUCATION = "Education"
    ENGINEERING = "Engineering"
    FACILITIES = "Facilities"
    FINANCE = "Finance & Accounting"
    HEALTH = "Health"
    HR = "Human Resources"
    LEGAL = "Legal"
    MANAGEMENT = "Management"
    OPERATIONS = "Operations"
    PLANNING = "Planning"
    POLICY = "Policy"
    SCIENCE = "Science"
    SOCIAL_SERVICES = "Social Services"
    TRADES = "Trades & Services"
    OTHER = "Other"


class Severity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def priority(self) -> int:
        """Get numeric priority for comparison."""
        return ["low", "medium", "high", "critical"].index(self.value)


class Frequency(str, Enum):
    """Alert delivery frequency."""

    DAILY = "daily"
    WEEKLY = "weekly"


class Job(BaseModel):
    """
    Represents a single job listing from the SJS job board.
    
    This is an immutable snapshot of a job at a point in time.
    """

    model_config = {"frozen": True}

    # Core identifiers (required)
    id: str = Field(..., description="Unique job ID from SJS")
    title: str = Field(..., min_length=1, description="Job title")
    employer: str = Field(..., min_length=1, description="Employer name")

    # Classification
    category: str | None = Field(None, description="Job category")
    classification: str | None = Field(None, description="Primary classification")
    sub_classification: str | None = Field(None, description="Secondary classification")
    job_type: str | None = Field(None, description="Employment type (e.g., Full-time)")

    # Location
    region: str | None = Field(None, description="Geographic region")
    area: str | None = Field(None, description="Specific area within region")

    # Description
    summary: str | None = Field(None, description="Short job summary")
    description: str | None = Field(None, description="Full job description")

    # Compensation
    pay_min: float | None = Field(None, ge=0, description="Minimum annual pay")
    pay_max: float | None = Field(None, ge=0, description="Maximum annual pay")

    # Dates
    posted_date: datetime | None = Field(None, description="Date job was posted")
    start_date: datetime | None = Field(None, description="Job start date")
    end_date: datetime | None = Field(None, description="Job end/closing date")

    # URL
    url: str | None = Field(None, description="Direct link to job posting")

    @field_validator("pay_max")
    @classmethod
    def pay_max_greater_than_min(cls, v: float | None, info: dict) -> float | None:
        """Ensure pay_max >= pay_min if both are set."""
        pay_min = info.data.get("pay_min")
        if v is not None and pay_min is not None and v < pay_min:
            raise ValueError(f"pay_max ({v}) must be >= pay_min ({pay_min})")
        return v

    def matches_region(self, region: Region | None) -> bool:
        """Check if job matches a region filter."""
        if region is None or region == Region.ALL:
            return True
        return self.region == region.value

    def matches_category(self, category: JobCategory | None) -> bool:
        """Check if job matches a category filter."""
        if category is None or category == JobCategory.ALL:
            return True
        return self.category == category.value


class Snapshot(BaseModel):
    """
    A point-in-time snapshot of all jobs scraped from the SJS board.
    
    Snapshots are immutable and stored as the basis for diff calculations.
    """

    model_config = {"frozen": True}

    timestamp: datetime = Field(..., description="When this snapshot was taken")
    jobs: list[Job] = Field(default_factory=list, description="All jobs in this snapshot")
    total_count: int = Field(..., description="Total number of jobs")
    scrape_duration_seconds: float | None = Field(
        None, ge=0, description="How long the scrape took"
    )
    source_url: str = Field(..., description="URL that was scraped")

    @field_validator("total_count")
    @classmethod
    def count_matches_jobs(cls, v: int, info: dict) -> int:
        """Ensure total_count matches actual job count."""
        jobs = info.data.get("jobs", [])
        if v != len(jobs):
            raise ValueError(f"total_count ({v}) != actual job count ({len(jobs)})")
        return v


class FieldChange(BaseModel):
    """Represents a change to a specific field in a job."""

    model_config = {"frozen": True}

    field: str = Field(..., description="Name of the field that changed")
    old_value: str | None = Field(None, description="Previous value")
    new_value: str | None = Field(None, description="New value")


class JobChange(BaseModel):
    """
    Represents a change to a job between two snapshots.
    
    Can represent:
    - New job (before is None)
    - Removed job (after is None)
    - Modified job (both set, with field changes)
    """

    model_config = {"frozen": True}

    job_id: str = Field(..., description="Job ID")
    before: Job | None = Field(None, description="Job state before change")
    after: Job | None = Field(None, description="Job state after change")
    changes: list[FieldChange] = Field(
        default_factory=list, description="Specific field changes"
    )

    @property
    def change_type(self) -> str:
        """Get human-readable change type."""
        if self.before is None:
            return "added"
        if self.after is None:
            return "removed"
        return "modified"

    @property
    def title(self) -> str:
        """Get job title (from after if available, otherwise before)."""
        if self.after:
            return self.after.title
        if self.before:
            return self.before.title
        return "Unknown"


class DiffResult(BaseModel):
    """Complete diff between two snapshots."""

    model_config = {"frozen": True}

    previous_snapshot: Snapshot = Field(..., description="Earlier snapshot")
    current_snapshot: Snapshot = Field(..., description="Later snapshot")
    added: list[JobChange] = Field(default_factory=list, description="Newly added jobs")
    removed: list[JobChange] = Field(default_factory=list, description="Removed jobs")
    modified: list[JobChange] = Field(default_factory=list, description="Modified jobs")

    @property
    def total_changes(self) -> int:
        """Total number of changes across all categories."""
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return self.total_changes > 0
