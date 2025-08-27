import logging
import requests

from ..config.settings import settings

MR_CALL_URL = "https://api.mrcall.ai/mrcall/v1/atom/d32b77ab-b8d5-30ce-afcb-0d477fd14279/outbound"

logger = logging.getLogger(__name__)


def start_call(phone_number: str) -> dict:
    """Trigger an outbound call via MrCall."""
    headers = {
        "Authorization": f"Basic {settings.mrcall_token}",
        "Content-Type": "application/json",
    }
    payload = {"toNumber": phone_number}
    logger.debug("MrCall request: %s", payload)
    response = requests.post(MR_CALL_URL, json=payload, headers=headers, timeout=10)
    logger.debug("MrCall response %s: %s", response.status_code, response.text)
    response.raise_for_status()
    return response.json()
