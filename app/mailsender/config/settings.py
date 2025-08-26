"""Application configuration loaded from ``settings.ini``.

This module defines the :class:`Settings` object which reads configuration
values from the project level ``settings.ini`` file. The file is expected to
contain a ``[settings]`` section with keys matching the fields defined in the
``Settings`` model below. Defaults are provided for all fields so the
application can run even when the file is missing or incomplete.

The loader searches upwards from this file's location to find
``settings.ini``. If it cannot be found, the defaults are used.
"""

from configparser import ConfigParser
from pathlib import Path
from typing import Dict

from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_key: str = "sk-dummy"
    sendgrid_key: str = "sendgrid-dummy"
    mrcall_user: str = "mrcall_user"
    mrcall_password: str = "mrcall_password"
    mrcall_business_id: str = "mrcall_business"
    email_prompt: str = (
        "Generate a JSON object with fields `recipient`, `subject`, and `body` "
        "for the recipient `{email_address}` using additional lead details "
        "`{custom_args}`. The body must be HTML."
    )
    database_url: str = "sqlite:///./mailsender.db"

def _load_from_ini() -> Dict[str, str]:
    """Load configuration values from the nearest ``settings.ini`` file."""
    config: Dict[str, str] = {}
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "settings.ini"
        if candidate.exists():
            parser = ConfigParser()
            parser.read(candidate)
            if parser.has_section("settings"):
                config = {k: v for k, v in parser.items("settings") if v}
            break
    return config


def get_settings() -> Settings:
    """Instantiate :class:`Settings` populated from ``settings.ini``."""
    return Settings(**_load_from_ini())


settings = get_settings()
