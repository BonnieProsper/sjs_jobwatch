from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """
    Configure application-wide logging.

    Call exactly once at process startup.
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
