"""
Configuration management for SJS JobWatch.

Handles environment variables, defaults, and path management.
"""

import os
from pathlib import Path

# ============================================================================
# Project Paths
# ============================================================================

# Find the project root (where pyproject.toml lives)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
EXPORT_DIR = DATA_DIR / "exports"
SUBSCRIPTIONS_FILE = PROJECT_ROOT / "subscriptions.json"
LOG_FILE = DATA_DIR / "jobwatch.log"

# ============================================================================
# SJS Job Board Configuration
# ============================================================================

# Base URL for the SJS job search page
SJS_BASE_URL = "https://www.sjs.govt.nz/jobs/search/"

# Default search parameters
DEFAULT_SEARCH_PARAMS = {
    "region": "All",
    "category": "All",
    "subcategory": "",
    "keyword": "",
}

# User-Agent to use for requests (be respectful)
USER_AGENT = "SJS-JobWatch/1.0 (Educational Project; +https://github.com/yourusername/sjs-jobwatch)"

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Delay between requests (seconds) - be respectful to the server
REQUEST_DELAY = 2.0

# ============================================================================
# Email Configuration
# ============================================================================

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

# Gmail credentials (required for sending emails)
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# From address for emails
EMAIL_FROM = GMAIL_ADDRESS or "noreply@sjsjobwatch.local"
EMAIL_FROM_NAME = "SJS JobWatch"

# ============================================================================
# Alert Configuration
# ============================================================================

# Default alert settings
DEFAULT_ALERT_FREQUENCY = "daily"
DEFAULT_ALERT_HOUR = 9  # 9 AM
DEFAULT_MIN_SEVERITY = "medium"
DEFAULT_ICT_ONLY = False

# Maximum number of jobs to include in email
MAX_JOBS_IN_EMAIL = 50

# ============================================================================
# Storage Configuration
# ============================================================================

# Keep snapshots for this many days (0 = keep forever)
SNAPSHOT_RETENTION_DAYS = 90

# Maximum number of snapshots to keep (0 = unlimited)
MAX_SNAPSHOTS = 1000

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# Feature Flags
# ============================================================================

# Enable experimental features
ENABLE_TRENDS = True
ENABLE_RECOMMENDATIONS = False  # Not implemented yet

# ============================================================================
# Helper Functions
# ============================================================================


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    for directory in (DATA_DIR, SNAPSHOT_DIR, EXPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def validate_email_config() -> tuple[bool, str]:
    """
    Validate that email configuration is complete.
    
    Returns:
        (is_valid, error_message)
    """
    if not GMAIL_ADDRESS:
        return False, "GMAIL_ADDRESS environment variable is not set"

    if not GMAIL_APP_PASSWORD:
        return False, "GMAIL_APP_PASSWORD environment variable is not set"

    if "@" not in GMAIL_ADDRESS:
        return False, "GMAIL_ADDRESS does not appear to be a valid email"

    return True, ""


def get_sjs_url(region: str = "All", category: str = "All", keyword: str = "") -> str:
    """
    Build a complete SJS search URL with parameters.
    
    Args:
        region: Region filter
        category: Category filter
        keyword: Search keyword
        
    Returns:
        Complete URL ready to scrape
    """
    # The SJS URL format might need adjustment based on actual site structure
    params = {
        "region": region,
        "category": category,
    }
    if keyword:
        params["keyword"] = keyword

    # Build query string
    query = "&".join(f"{k}={v}" for k, v in params.items() if v and v != "All")

    if query:
        return f"{SJS_BASE_URL}?{query}"
    return SJS_BASE_URL
