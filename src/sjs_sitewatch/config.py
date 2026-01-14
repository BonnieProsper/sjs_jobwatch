from __future__ import annotations

"""
Central configuration defaults for sjs_sitewatch.

This module is intentionally minimal, import-safe, and side-effect free.
"""

import os
from pathlib import Path

# -------------------------
# Project paths
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
# Defaults / filters
# -------------------------

DEFAULT_REGION: str | None = None
DEFAULT_ICT_ONLY: bool = True


# -------------------------
# Email / SMTP
# -------------------------

SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

GMAIL_ADDRESS: str | None = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD: str | None = os.getenv("GMAIL_APP_PASSWORD")
