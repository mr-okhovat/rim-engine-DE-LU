from __future__ import annotations

import logging
import os
import sys


def setup_logging(level: str | None = None) -> None:
    """
    Configure consistent logging for CLI/scripts.

    - Default level: INFO
    - Can be overridden by LOG_LEVEL env var or explicit argument.
    - Logs to stdout with timestamps for operational traceability.
    """
    lvl = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, lvl, logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
