import base64
import logging
import requests

from ..config.settings import settings

MR_CALL_URL = f"https://api.mrcall.ai/mrcall/v1/atom/{settings.mrcall_business_id}/outbound"

logger = logging.getLogger(__name__)


def start_call(phone_number: str) -> dict:
    """Trigger an outbound call via MrCall."""
    credentials = f"{settings.mrcall_username}:{settings.mrcall_password}".encode()
    token = base64.b64encode(credentials).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    payload = {"toNumber": phone_number}
    logger.debug("MrCall request: %s", payload)
    response = requests.post(MR_CALL_URL, json=payload, headers=headers, timeout=10)
    logger.debug("MrCall response %s: %s", response.status_code, response.text)
    response.raise_for_status()
    return response.json()
