"""Application configuration loaded from ``settings.ini``.

This module defines the :class:`Settings` object which reads configuration
values from ``app/resources/settings.ini``. The file is expected to contain a
``[settings]`` section with keys matching the fields defined in the
``Settings`` model below. Defaults are provided for all fields so the
application can run even when the file is missing or incomplete.

Only ``app/resources/settings.ini`` is considered; other ``settings.ini``
files are ignored. If the file is absent, the defaults are used.
"""

from configparser import ConfigParser
from pathlib import Path
from typing import Dict

from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_key: str = "sk-dummy"
    openai_model: str = "gpt-5-mini"
    sendgrid_key: str = "sendgrid-dummy"
    from_name: str = "SG Test"
    mrcall_username: str = "mrcall_username"
    mrcall_password: str = "mrcall_password"
    mrcall_business_id: str = "mrcall_business"
    email_prompt: str = (
        "Sei un assistente che scrive email molto semplici e naturali. "
        "Crea il corpo della mail per {email_address} usando i dati del lead: {custom_args}"
    )
    database_url: str = "sqlite:///./mailsender.db"
    body: str = ""

def _load_from_ini() -> Dict[str, str]:
    """Load configuration values from ``app/resources/settings.ini``."""
    config: Dict[str, str] = {}
    candidate = Path(__file__).resolve().parents[2] / "resources" / "settings.ini"
    if candidate.exists():
        parser = ConfigParser()
        parser.read(candidate)
        if parser.has_section("settings"):
            for k, v in parser.items("settings"):
                if not v and k != "body":
                    continue
                if k == "database_url" and v.startswith("sqlite:///"):
                    db_path = v.replace("sqlite:///", "")
                    if not Path(db_path).is_absolute():
                        db_path = (candidate.parent / db_path).resolve()
                    config[k] = f"sqlite:///{db_path}"
                else:
                    config[k] = v
    return config


def get_settings() -> Settings:
    """Instantiate :class:`Settings` populated from ``settings.ini``."""
    return Settings(**_load_from_ini())


settings = get_settings()
