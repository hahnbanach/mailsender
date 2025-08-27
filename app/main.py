"""Main application entry point."""

from __future__ import annotations

import logging
import os

from mailsender.api.main import app


log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))


if __name__ == "__main__":
    import argparse
    import logging
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=log_level.lower())
