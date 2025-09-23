"""Main application entry point."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from mailsender.api.main import app


def _configure_logging(level: str | None) -> str:
    """Configure the root logger and return the effective level name."""

    resolved_level = (level or "info").upper()
    numeric_level = getattr(logging, resolved_level, logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(levelname)s: %(message)s",
        force=True,
    )
    logging.getLogger().setLevel(numeric_level)
    logging.info("info messages enabled")
    logging.debug("debug messages enabled")
    return logging.getLevelName(numeric_level).lower()


env_level = os.getenv("LOG_LEVEL")
if env_level:
    _configure_logging(env_level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the API server")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()

    requested_level = "debug" if args.debug else (env_level or "info")
    log_level = _configure_logging(requested_level)

    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=log_level)
