"""
Central configuration defaults for sjs_sitewatch.

This module is intentionally minimal and filesystem-safe.
"""

from pathlib import Path


# -------------------------
# Paths
# -------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
EXPORT_DIR = DATA_DIR / "exports"


def ensure_directories() -> None:
    """
    Ensure required directories exist.
    Safe to call multiple times.
    """
    for path in (DATA_DIR, SNAPSHOT_DIR, EXPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)


# -------------------------
# Defaults
# -------------------------

DEFAULT_REGION: str | None = None
DEFAULT_ICT_ONLY: bool = False
