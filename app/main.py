"""Main application entry point."""

from __future__ import annotations

import argparse
import logging
import os

from mailsender.api.main import app


def _configure_logging(level: str | None) -> str:
    """Configure the root logger and return the effective level."""
    if level:
        level = level.lower()
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO), force=True
        )
        logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
        return level
    return "info"


env_level = os.getenv("LOG_LEVEL")
if env_level:
    _configure_logging(env_level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the API server")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()

    log_level = "debug" if args.debug else (env_level or "info")
    _configure_logging(log_level)

    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=log_level)
